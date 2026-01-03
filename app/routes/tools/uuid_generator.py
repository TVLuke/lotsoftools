from flask import Blueprint, render_template, request
import json
import os
from app.services.link_service import increment_click_count

uuid_generator_bp = Blueprint('uuid_generator', __name__, url_prefix='/tools')

@uuid_generator_bp.route('/uuid-generator')
def index():
    # Track click
    increment_click_count(request.path)
    
    return render_template('tools/uuid_generator.html')
