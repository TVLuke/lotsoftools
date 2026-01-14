from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count
from app.utils import require_tool_active

icon_finder_bp = Blueprint('icon_finder', __name__, url_prefix='/tools')

@icon_finder_bp.route('/icon-finder')
@require_tool_active('icon_finder')
def index():
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'icon_finder_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/icon_finder.html', tool_data=tool_data)
