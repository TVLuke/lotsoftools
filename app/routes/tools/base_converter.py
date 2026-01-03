from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

base_converter_bp = Blueprint('base_converter', __name__, url_prefix='/tools')

@base_converter_bp.route('/base-converter')
def index():
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'base_converter_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/base_converter.html', tool_data=tool_data)
