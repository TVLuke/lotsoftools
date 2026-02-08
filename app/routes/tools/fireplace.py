from flask import Blueprint, render_template, request
from app.services.link_service import increment_click_count
import json
import os

fireplace_bp = Blueprint('fireplace', __name__)

def load_tool_data():
    """Load tool data from JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), 'fireplace_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@fireplace_bp.route('/tools/fireplace')
def fireplace():
    increment_click_count(request.path)
    tool_data = load_tool_data()
    return render_template('tools/fireplace.html', tool_data=tool_data)
