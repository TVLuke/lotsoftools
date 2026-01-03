from flask import Blueprint, render_template
import json
import os

date_calculator_bp = Blueprint('date_calculator', __name__)

def load_tool_data(mode='since'):
    if mode == 'until':
        json_path = os.path.join(os.path.dirname(__file__), 'date_calculator_until_tool.json')
    else:
        json_path = os.path.join(os.path.dirname(__file__), 'date_calculator_tool.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@date_calculator_bp.route('/tools/time-since')
def time_since():
    from app.models import Link
    from app import db
    link = Link.query.filter_by(url='/tools/time-since').first()
    if link:
        link.click_count += 1
        db.session.commit()
    
    tool_data = load_tool_data('since')
    return render_template('tools/date_calculator.html', tool_data=tool_data, mode='since')

@date_calculator_bp.route('/tools/time-until')
def time_until():
    from app.models import Link
    from app import db
    link = Link.query.filter_by(url='/tools/time-until').first()
    if link:
        link.click_count += 1
        db.session.commit()
    
    tool_data = load_tool_data('until')
    return render_template('tools/date_calculator.html', tool_data=tool_data, mode='until')
