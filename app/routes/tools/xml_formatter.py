from flask import Blueprint, render_template, request
from app.services.link_service import increment_click_count

xml_formatter_bp = Blueprint('xml_formatter', __name__, url_prefix='/tools')

@xml_formatter_bp.route('/xml-formatter')
def index():
    increment_click_count(request.path)
    return render_template('tools/xml_formatter.html')
