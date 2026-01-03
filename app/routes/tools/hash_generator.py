from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

hash_generator_bp = Blueprint('hash_generator', __name__, url_prefix='/tools')

@hash_generator_bp.route('/hash-generator')
def index():
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'hash_generator_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/hash_generator.html', tool_data=tool_data)
