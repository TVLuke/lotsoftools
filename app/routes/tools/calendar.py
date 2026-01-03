from flask import Blueprint, render_template, request
from app.services.link_service import increment_click_count

calendar_bp = Blueprint('calendar', __name__, url_prefix='/tools')

@calendar_bp.route('/calendar')
def index():
    increment_click_count(request.path)
    return render_template('tools/calendar.html')
