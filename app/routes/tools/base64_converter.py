from flask import Blueprint, render_template, g
from app.services.link_service import increment_click_count
import json
import os

base64_bp = Blueprint('base64', __name__)

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'base64_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@base64_bp.route('/tools/base64')
def base64_converter():
    increment_click_count('/tools/base64')
    
    tool_data = load_tool_data()
    current_lang = g.get('lang', 'en')
    
    return render_template('tools/base64.html', 
                          tool_data=tool_data,
                          current_lang=current_lang)
