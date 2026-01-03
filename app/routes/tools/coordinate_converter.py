from flask import Blueprint, render_template, g
from app.services.link_service import increment_click_count
import json
import os

coordinate_converter_bp = Blueprint('coordinate_converter', __name__)

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'coordinate_converter_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@coordinate_converter_bp.route('/tools/coordinates')
def coordinates():
    increment_click_count('/tools/coordinates')
    
    tool_data = load_tool_data()
    current_lang = g.get('lang', 'en')
    
    return render_template('tools/coordinate_converter.html', 
                          tool_data=tool_data,
                          current_lang=current_lang)
