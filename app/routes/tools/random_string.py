from flask import Blueprint, render_template, request
from app.services.link_service import increment_click_count

random_string_bp = Blueprint('random_string', __name__, url_prefix='/tools')

@random_string_bp.route('/random-string')
def index():
    increment_click_count(request.path)
    return render_template('tools/random_string.html')
