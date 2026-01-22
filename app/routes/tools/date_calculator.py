from flask import Blueprint, render_template
import json
import os
from app.services.link_service import increment_click_count

date_calculator_bp = Blueprint('date_calculator', __name__)

def load_tool_data(mode='since'):
    if mode == 'until':
        json_path = os.path.join(os.path.dirname(__file__), 'date_calculator_until_tool.json')
    elif mode == 'between':
        json_path = os.path.join(os.path.dirname(__file__), 'date_calculator_between_tool.json')
    else:
        json_path = os.path.join(os.path.dirname(__file__), 'date_calculator_tool.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@date_calculator_bp.route('/tools/time-since')
def time_since():
    increment_click_count('/tools/time-since')
    tool_data = load_tool_data('since')
    return render_template('tools/date_calculator.html', tool_data=tool_data, mode='since')

@date_calculator_bp.route('/tools/time-until')
def time_until():
    increment_click_count('/tools/time-until')
    tool_data = load_tool_data('until')
    return render_template('tools/date_calculator.html', tool_data=tool_data, mode='until')

@date_calculator_bp.route('/tools/time-between')
def time_between():
    increment_click_count('/tools/time-between')
    tool_data = load_tool_data('between')
    return render_template('tools/date_calculator.html', tool_data=tool_data, mode='between')
