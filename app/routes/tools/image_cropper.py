from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

image_cropper_bp = Blueprint('image_cropper', __name__, url_prefix='/tools')

@image_cropper_bp.route('/image-cropper')
def index():
    increment_click_count(request.path)

    json_path = os.path.join(os.path.dirname(__file__), 'image_cropper_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)

    return render_template('tools/image_cropper.html', tool_data=tool_data)
