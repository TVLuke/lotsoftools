from flask import Blueprint, render_template, request, session
from app.services.link_service import increment_click_count
import os
import json

calendar_bp = Blueprint('calendar', __name__, url_prefix='/tools')

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'calendar_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@calendar_bp.route('/calendar')
def index():
    increment_click_count(request.path)
    tool_data = load_tool_data()
    current_lang = session.get('lang', 'en')
    return render_template('tools/calendar.html',
                          tool_data=tool_data,
                          current_lang=current_lang)
