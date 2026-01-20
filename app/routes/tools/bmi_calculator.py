from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

bmi_calculator_bp = Blueprint('bmi_calculator', __name__, url_prefix='/tools')


@bmi_calculator_bp.route('/bmi-calculator')
def index():
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'bmi_calculator_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/bmi_calculator.html', tool_data=tool_data)
