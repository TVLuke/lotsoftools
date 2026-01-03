from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

unit_converter_bp = Blueprint('unit_converter', __name__, url_prefix='/tools')

@unit_converter_bp.route('/unit-converter')
def index():
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'unit_converter_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/unit_converter.html', tool_data=tool_data)
