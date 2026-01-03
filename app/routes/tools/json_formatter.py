from flask import Blueprint, render_template, request
from app.services.link_service import increment_click_count

json_formatter_bp = Blueprint('json_formatter', __name__, url_prefix='/tools')

@json_formatter_bp.route('/json-formatter')
def index():
    increment_click_count(request.path)
    return render_template('tools/json_formatter.html')
