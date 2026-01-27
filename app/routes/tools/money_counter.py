from flask import Blueprint, render_template, session
from app.services.link_service import increment_click_count
import os
import json

money_counter_bp = Blueprint('money_counter', __name__, url_prefix='/tools')

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'money_counter_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@money_counter_bp.route('/money-counter')
def index():
    increment_click_count('/tools/money-counter')
    tool_data = load_tool_data()
    current_lang = session.get('lang', 'en')
    return render_template('tools/money_counter.html',
                          tool_data=tool_data,
                          current_lang=current_lang)
