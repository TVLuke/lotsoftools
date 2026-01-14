from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

map_tracer_bp = Blueprint('map_tracer', __name__, url_prefix='/tools')

@map_tracer_bp.route('/map-tracer')
def index():
    # Track click
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'map_tracer_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/map_tracer.html', tool_data=tool_data)
