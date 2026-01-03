from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

yaml_formatter_bp = Blueprint('yaml_formatter', __name__, url_prefix='/tools')


@yaml_formatter_bp.route('/yaml-formatter')
def index():
    increment_click_count(request.path)

    json_path = os.path.join(os.path.dirname(__file__), 'yaml_formatter_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)

    return render_template('tools/yaml_formatter.html', tool_data=tool_data)
