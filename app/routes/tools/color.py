import json
import os
import random
from flask import Blueprint, render_template, redirect, url_for, request, session
from app.services.link_service import increment_click_count

color_bp = Blueprint('color', __name__, url_prefix='/tools')

tool_json_path = os.path.join(os.path.dirname(__file__), 'color_tool.json')
with open(tool_json_path, 'r', encoding='utf-8') as f:
    tool_data = json.load(f)

def generate_random_hex_color():
    """Generate a random hex color."""
    return '{:06X}'.format(random.randint(0, 0xFFFFFF))

@color_bp.route('/color')
def index():
    # Redirect to a random color
    return redirect(url_for('color.show_color', hex_color=generate_random_hex_color()))

@color_bp.route('/color/<hex_color>')
def show_color(hex_color):
    increment_click_count('/tools/color')
    current_lang = session.get('lang', 'en')
    
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Validate hex color (3 or 6 characters)
    if not (len(hex_color) in [3, 6] and all(c in '0123456789ABCDEFabcdef' for c in hex_color)):
        return redirect(url_for('color.show_color', hex_color='4A90E2'))
    
    # Expand 3-char hex to 6-char
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    return render_template('tools/color.html', hex_color=hex_color.upper(), tool_data=tool_data, current_lang=current_lang)
