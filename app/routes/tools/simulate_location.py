from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

simulate_location_bp = Blueprint('simulate_location', __name__, url_prefix='/tools')

@simulate_location_bp.route('/simulate-location')
def index():
    # Track click
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'simulate_location_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/simulate_location.html', tool_data=tool_data)
