from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

map_maker_bp = Blueprint('map_maker', __name__, url_prefix='/tools')

@map_maker_bp.route('/map-maker')
def index():
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'map_maker_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/map_maker.html', tool_data=tool_data)
