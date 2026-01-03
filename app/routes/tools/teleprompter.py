from flask import Blueprint, render_template, g
from app.services.link_service import increment_click_count
import json
import os

teleprompter_bp = Blueprint('teleprompter', __name__)

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'teleprompter_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@teleprompter_bp.route('/tools/teleprompter')
def teleprompter():
    increment_click_count('/tools/teleprompter')
    
    tool_data = load_tool_data()
    current_lang = g.get('lang', 'en')
    
    return render_template('tools/teleprompter.html', 
                          tool_data=tool_data,
                          current_lang=current_lang)
