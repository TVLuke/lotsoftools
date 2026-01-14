from flask import Blueprint, render_template, request, session
from app.services.link_service import increment_click_count
import json
import os

csv_table_bp = Blueprint('csv_table', __name__, url_prefix='/tools')

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'csv_table_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@csv_table_bp.route('/csv-table')
def index():
    increment_click_count(request.path)
    tool_data = load_tool_data()
    current_lang = session.get('lang', 'en')
    return render_template('tools/csv_table.html', 
                          tool_data=tool_data,
                          current_lang=current_lang)
