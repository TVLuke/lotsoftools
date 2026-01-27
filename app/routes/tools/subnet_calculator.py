from flask import Blueprint, render_template, session
from app.services.link_service import increment_click_count
import os
import json

subnet_calculator_bp = Blueprint('subnet_calculator', __name__)

def load_tool_data(mode='ipv4'):
    if mode == 'ipv6':
        json_path = os.path.join(os.path.dirname(__file__), 'subnet_calculator_ipv6_tool.json')
    else:
        json_path = os.path.join(os.path.dirname(__file__), 'subnet_calculator_ipv4_tool.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@subnet_calculator_bp.route('/tools/subnet-calculator-ipv4')
def ipv4():
    increment_click_count('/tools/subnet-calculator-ipv4')
    tool_data = load_tool_data('ipv4')
    current_lang = session.get('lang', 'en')
    return render_template('tools/subnet_calculator.html', 
                          tool_data=tool_data, 
                          mode='ipv4',
                          current_lang=current_lang)

@subnet_calculator_bp.route('/tools/subnet-calculator-ipv6')
def ipv6():
    increment_click_count('/tools/subnet-calculator-ipv6')
    tool_data = load_tool_data('ipv6')
    current_lang = session.get('lang', 'en')
    return render_template('tools/subnet_calculator.html', 
                          tool_data=tool_data, 
                          mode='ipv6',
                          current_lang=current_lang)
