from flask import Blueprint, render_template, redirect, url_for, request
from app.services.link_service import increment_click_count

color_bp = Blueprint('color', __name__, url_prefix='/tools')

@color_bp.route('/color')
def index():
    # Default to a nice blue color
    return redirect(url_for('color.show_color', hex_color='4A90E2'))

@color_bp.route('/color/<hex_color>')
def show_color(hex_color):
    increment_click_count('/tools/color')
    
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Validate hex color (3 or 6 characters)
    if not (len(hex_color) in [3, 6] and all(c in '0123456789ABCDEFabcdef' for c in hex_color)):
        return redirect(url_for('color.show_color', hex_color='4A90E2'))
    
    # Expand 3-char hex to 6-char
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    return render_template('tools/color.html', hex_color=hex_color.upper())
