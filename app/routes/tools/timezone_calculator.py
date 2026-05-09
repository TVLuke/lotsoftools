import json
import os
from flask import Blueprint, render_template, session

from app.services.link_service import increment_click_count

timezone_calculator_bp = Blueprint('timezone_calculator', __name__)

tool_json_path = os.path.join(os.path.dirname(__file__), 'timezone_calculator_tool.json')
with open(tool_json_path, 'r') as f:
    tool_data = json.load(f)


@timezone_calculator_bp.route('/tools/timezone-calculator')
def timezone_calculator():
    increment_click_count('/tools/timezone-calculator')
    lang = session.get('lang', 'en')
    return render_template('tools/timezone_calculator.html', tool_data=tool_data, current_lang=lang)
