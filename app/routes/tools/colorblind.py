from flask import Blueprint, render_template, request, g
from app.services.link_service import increment_click_count
import json
import os

colorblind_bp = Blueprint('colorblind', __name__, url_prefix='/tools')

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'colorblind_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@colorblind_bp.route('/colorblind-simulator')
def index():
    increment_click_count(request.path)
    tool_data = load_tool_data()
    current_lang = g.get('lang', 'en')
    return render_template('tools/colorblind.html',
                          tool_data=tool_data,
                          current_lang=current_lang)
