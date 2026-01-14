from flask import Blueprint, render_template, session
from app.services.link_service import increment_click_count
import json
import os

ascii_table_bp = Blueprint('ascii_table', __name__)

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'ascii_table_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@ascii_table_bp.route('/tools/ascii')
def ascii_table():
    increment_click_count('/tools/ascii')
    
    tool_data = load_tool_data()
    current_lang = session.get('lang', 'en')
    
    return render_template('tools/ascii_table.html', 
                          tool_data=tool_data,
                          current_lang=current_lang)
