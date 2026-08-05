from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

giro_code_bp = Blueprint('giro_code', __name__, url_prefix='/tools')

@giro_code_bp.route('/giro-code')
def index():
    increment_click_count(request.path)

    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'giro_code_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)

    return render_template('tools/giro_code.html', tool_data=tool_data)
