from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

diff_tool_bp = Blueprint('diff_tool', __name__, url_prefix='/tools')

@diff_tool_bp.route('/diff')
def index():
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'diff_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/diff_tool.html', tool_data=tool_data)
