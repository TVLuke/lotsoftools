"""Cookie consent routes for JavaScript-capable user detection."""

import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.bot_detection import is_bot_request

# Create blueprint
cookie_consent_bp = Blueprint('cookie_consent', __name__)

# Log file for JavaScript-capable users
JS_CAPABLE_LOG_FILE = 'logs/js_capable_users.log'

def _ensure_log_dir():
    """Ensure log directory exists."""
    log_dir = os.path.dirname(JS_CAPABLE_LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

def log_js_capable_user(user_agent, url=None):
    """Log a user that has JavaScript capabilities and cookies.
    
    This is a strong signal of human behavior since:
    1. JavaScript executed successfully
    2. Cookies are enabled
    3. User interacted with the site
    """
    try:
        _ensure_log_dir()
        timestamp = datetime.now().isoformat()
        
        # Get current bot detection info
        is_bot, bot_reason = is_bot_request()
        
        # Sanitize inputs
        ua_clean = user_agent.replace('\n', ' ').replace('|', ' ')[:500]
        url_clean = (url or request.referrer or '').replace('|', ' ')[:100]
        reason_clean = (bot_reason or '')[:100]
        
        # Log format: timestamp|BOT_DETECTION_RESULT|url|user_agent|bot_reason
        log_entry = f"{timestamp}|{'BOT' if is_bot else 'HUMAN_BY_UA'}|{url_clean}|{ua_clean}|{reason_clean}\n"
        
        with open(JS_CAPABLE_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        return True
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to log JS-capable user: {e}")
        return False

@cookie_consent_bp.route('/api/js-capable', methods=['POST'])
def log_js_capable():
    """Log JavaScript-capable user.
    
    This endpoint is called when:
    1. User has existing cookies (returning visitor with JS)
    2. Banner is shown to new user (proves JS execution)
    
    Both cases indicate JavaScript execution - strong human signal.
    """
    try:
        # Get user agent and other info
        user_agent = request.headers.get('User-Agent', '')
        url = request.json.get('url') if request.is_json else request.referrer
        
        # Log this as a JavaScript-capable user
        log_js_capable_user(user_agent, url)
        
        return jsonify({
            'success': True,
            'message': 'JavaScript capability recorded'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
