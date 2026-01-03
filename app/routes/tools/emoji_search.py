from flask import Blueprint, jsonify, render_template, request
import json
import os

from app.services.emoji_search import SUPPORTED_LANGS, search_emojis
from app.services.link_service import increment_click_count


emoji_search_bp = Blueprint('emoji_search', __name__, url_prefix='/tools')


@emoji_search_bp.route('/emoji-search')
def index():
    increment_click_count(request.path)

    json_path = os.path.join(os.path.dirname(__file__), 'emoji_search_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)

    return render_template(
        'tools/emoji_search.html',
        tool_data=tool_data,
        supported_langs=SUPPORTED_LANGS,
    )


@emoji_search_bp.route('/emoji-search/query', methods=['POST'])
def query():
    data = request.get_json(silent=True) or {}

    q = (data.get('q') or '').strip()
    lang = (data.get('lang') or 'all').strip()
    limit = data.get('limit', 200)
    offset = data.get('offset', 0)

    try:
        result = search_emojis(q, lang=lang, limit=limit, offset=offset)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500
