"""Cookie consent routes for JavaScript-capable user detection."""

import os
import json
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from app.services.bot_detection import is_bot_request

# Create blueprint
cookie_consent_bp = Blueprint('cookie_consent', __name__)

# Log files for JavaScript-capable users and failed attempts (in data/ for Docker volume persistence)
JS_CAPABLE_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'js_capable_users.log')
FAILED_API_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'failed_js_api_calls.log')

def _ensure_log_dir():
    """Ensure log directory exists."""
    log_dir = os.path.dirname(JS_CAPABLE_LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

def generate_js_nonce():
    """Generate a nonce for JavaScript capability verification.
    
    This nonce is stored in the session and must be returned by the client
    to prove they actually loaded the page with JavaScript enabled.
    """
    nonce = secrets.token_urlsafe(32)
    
    # Store nonce with timestamp in session
    if 'js_nonces' not in session:
        session['js_nonces'] = {}
    
    session['js_nonces'][nonce] = {
        'created': datetime.utcnow().isoformat(),
        'used': False
    }
    
    # Clean up old nonces (older than 1 hour)
    _cleanup_old_nonces()
    
    return nonce

def validate_js_nonce(nonce):
    """Validate that the nonce was generated for this session.
    
    Returns True if valid and marks as used to prevent replay attacks.
    """
    if 'js_nonces' not in session or nonce not in session['js_nonces']:
        return False
    
    nonce_data = session['js_nonces'][nonce]
    
    # Check if already used (replay protection)
    if nonce_data.get('used', False):
        return False
    
    # Check age (should be used within 5 minutes)
    created_time = datetime.fromisoformat(nonce_data['created'])
    if datetime.utcnow() - created_time > timedelta(minutes=5):
        return False
    
    # Mark as used
    nonce_data['used'] = True
    session['js_nonces'][nonce] = nonce_data
    
    return True

def _cleanup_old_nonces():
    """Clean up old nonces from session."""
    if 'js_nonces' not in session:
        return
    
    current_time = datetime.utcnow()
    nonces_to_remove = []
    
    for nonce, data in session['js_nonces'].items():
        created_time = datetime.fromisoformat(data['created'])
        # Remove nonces older than 1 hour
        if current_time - created_time > timedelta(hours=1):
            nonces_to_remove.append(nonce)
    
    for nonce in nonces_to_remove:
        del session['js_nonces'][nonce]

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
        
        # Sanitize inputs - remove newlines and pipe characters from all parts
        import re
        def sanitize(text):
            if not text:
                return text
            # Remove all types of whitespace and problematic characters
            text = re.sub(r'[\n\r\t|]', ' ', str(text))
            # Replace multiple spaces with single space
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        
        timestamp_clean = sanitize(timestamp)
        ua_clean = sanitize(user_agent)[:500]
        url_clean = sanitize(url or request.referrer or '')[:100]
        reason_clean = sanitize(bot_reason or '')[:100]
        
        # Log format: timestamp|BOT_DETECTION_RESULT|url|user_agent|bot_reason
        log_entry = f"{timestamp_clean}|{'BOT' if is_bot else 'HUMAN_BY_UA'}|{url_clean}|{ua_clean}|{reason_clean}\n"
        
        with open(JS_CAPABLE_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        return True
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to log JS-capable user: {e}")
        return False

def log_failed_api_attempt(reason, user_agent, nonce_status):
    """Log failed API attempts for security monitoring.
    
    Args:
        reason: Why the attempt failed (INVALID_NONCE, MISSING_NONCE, etc.)
        user_agent: The User-Agent header from the request
        nonce_status: Status of the nonce (missing, invalid, used, expired)
    """
    try:
        _ensure_log_dir()
        timestamp = datetime.now().isoformat()
        
        # Get client IP for security monitoring
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        
        # Sanitize inputs
        import re
        def sanitize(text):
            if not text:
                return text
            text = re.sub(r'[\n\r\t|]', ' ', str(text))
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        
        timestamp_clean = sanitize(timestamp)
        ua_clean = sanitize(user_agent)[:500]
        ip_clean = sanitize(client_ip)[:45]  # IPv6 can be long
        reason_clean = sanitize(reason)[:50]
        nonce_clean = sanitize(nonce_status)[:50]
        
        # Log format: timestamp|reason|user_agent|ip_address|nonce_status
        log_entry = f"{timestamp_clean}|{reason_clean}|{ua_clean}|{ip_clean}|{nonce_clean}\n"
        
        with open(FAILED_API_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        return True
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to log failed API attempt: {e}")
        return False

@cookie_consent_bp.route('/api/js-nonce', methods=['GET'])
def get_js_nonce():
    """Generate a nonce for JavaScript capability verification.
    
    This endpoint should be called when the page loads to get a fresh nonce
    that must be returned to the /api/js-capable endpoint.
    """
    try:
        nonce = generate_js_nonce()
        return jsonify({
            'success': True,
            'nonce': nonce
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to generate nonce'
        }), 500

@cookie_consent_bp.route('/api/js-capable', methods=['POST'])
def log_js_capable():
    """Log JavaScript-capable user.
    
    This endpoint is called when:
    1. User has existing cookies (returning visitor with JS)
    2. Banner is shown to new user (proves JS execution)
    
    Both cases indicate JavaScript execution - strong human signal.
    
    Requires a valid nonce to prevent direct API abuse.
    """
    try:
        # Get user agent for logging
        user_agent = request.headers.get('User-Agent', '')
        
        # Get nonce from request
        nonce = request.json.get('nonce') if request.is_json else None
        
        # Validate nonce - prevents direct API calls without page load
        if not nonce:
            log_failed_api_attempt('MISSING_NONCE', user_agent, 'missing')
            return jsonify({
                'success': False,
                'error': 'Invalid or missing nonce'
            }), 400
        
        if not validate_js_nonce(nonce):
            # Determine why validation failed
            if 'js_nonces' not in session or nonce not in session.get('js_nonces', {}):
                nonce_status = 'invalid'
            else:
                nonce_data = session['js_nonces'][nonce]
                if nonce_data.get('used', False):
                    nonce_status = 'used'
                else:
                    # Check if expired
                    created_time = datetime.fromisoformat(nonce_data['created'])
                    if datetime.utcnow() - created_time > timedelta(minutes=5):
                        nonce_status = 'expired'
                    else:
                        nonce_status = 'invalid'
            
            log_failed_api_attempt('INVALID_NONCE', user_agent, nonce_status)
            return jsonify({
                'success': False,
                'error': 'Invalid or missing nonce'
            }), 400
        
        # Get URL from request
        url = request.json.get('url') if request.is_json else request.referrer
        
        # Log this as a JavaScript-capable user
        log_js_capable_user(user_agent, url)
        
        return jsonify({
            'success': True,
            'message': 'JavaScript capability recorded'
        })
        
    except Exception as e:
        # Log the exception for debugging
        log_failed_api_attempt('EXCEPTION', request.headers.get('User-Agent', ''), 'error')
        return jsonify({
            'success': False,
            'error': 'Failed to record JavaScript capability'
        }), 500
