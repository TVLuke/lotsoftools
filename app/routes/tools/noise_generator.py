from flask import Blueprint, render_template, session
from app.services.link_service import increment_click_count
import json
import os

noise_generator_bp = Blueprint('noise_generator', __name__)

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'noise_generator_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@noise_generator_bp.route('/tools/noise-generator')
def noise_generator():

    increment_click_count('/tools/noise-generator')
    
    tool_data = load_tool_data()
    current_lang = session.get('lang', 'en')
    
    return render_template('tools/noise_generator.html',
                         tool_data=tool_data,
                         current_lang=current_lang)
