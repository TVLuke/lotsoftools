from flask import Blueprint, render_template, session
from app.services.link_service import increment_click_count
import json
import os

clock_bp = Blueprint('clock', __name__)

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'clock_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@clock_bp.route('/tools/clock')
def clock():
    increment_click_count('/tools/clock')
    
    tool_data = load_tool_data()
    current_lang = session.get('lang', 'en')
    
    return render_template('tools/clock.html', 
                          tool_data=tool_data,
                          current_lang=current_lang)
