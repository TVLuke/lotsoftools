from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

iban_validator_bp = Blueprint('iban_validator', __name__, url_prefix='/tools')

@iban_validator_bp.route('/iban-validator')
def index():
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'iban_validator_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/iban_validator.html', tool_data=tool_data)
