import json
import os
from flask import Blueprint, render_template, session

from app.services.link_service import increment_click_count

time_converter_bp = Blueprint('time_converter', __name__)

tool_json_path = os.path.join(os.path.dirname(__file__), 'time_converter_tool.json')
with open(tool_json_path, 'r') as f:
    tool_data = json.load(f)


@time_converter_bp.route('/tools/time-converter')
def time_converter():
    increment_click_count('/tools/time-converter')
    lang = session.get('lang', 'en')
    return render_template('tools/time_converter.html', tool_data=tool_data, current_lang=lang)
