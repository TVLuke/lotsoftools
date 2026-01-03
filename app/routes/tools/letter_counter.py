from flask import Blueprint, render_template, request
from app.services.link_service import increment_click_count

letter_counter_bp = Blueprint('letter_counter', __name__, url_prefix='/tools')

@letter_counter_bp.route('/letter-counter')
def index():
    increment_click_count(request.path)
    return render_template('tools/letter_counter.html')
