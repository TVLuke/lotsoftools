from flask import Blueprint, render_template, request, session
from app.services.link_service import increment_click_count
import os
import json

json_formatter_bp = Blueprint('json_formatter', __name__, url_prefix='/tools')

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'json_formatter_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@json_formatter_bp.route('/json-formatter')
def index():
    increment_click_count(request.path)
    tool_data = load_tool_data()
    current_lang = session.get('lang', 'en')
    return render_template('tools/json_formatter.html',
                          tool_data=tool_data,
                          current_lang=current_lang)
