from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

lorem_ipsum_bp = Blueprint('lorem_ipsum', __name__, url_prefix='/tools')

@lorem_ipsum_bp.route('/lorem-ipsum')
def index():
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'lorem_ipsum_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/lorem_ipsum.html', tool_data=tool_data)
