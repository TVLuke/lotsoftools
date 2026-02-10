from flask import Blueprint, render_template, request, jsonify, session
import requests
import time
import json
import os
from urllib.parse import urlparse
from app.services.link_service import increment_click_count
from app.services.blocklist_service import is_url_blocked, log_blocked_request, get_blocklist_info

redirect_follower_bp = Blueprint('redirect_follower', __name__, url_prefix='/tools')

# Request timeout in seconds
REQUEST_TIMEOUT = 10
# Maximum number of redirects to follow
MAX_REDIRECTS = 20

def follow_redirects(url, user_agent='Mozilla/5.0 (compatible; RedirectFollower/1.0)'):
    """Follow redirects until we reach the final URL or hit MAX_REDIRECTS."""
    
    result = {
        'initial_url': url,
        'redirect_chain': [],
        'final_url': None,
        'final_status': None,
        'total_redirects': 0,
        'error': None,
        'blocked': False
    }
    
    try:
        # Check if URL is blocked
        is_blocked, matched_domain = is_url_blocked(url)
        if is_blocked:
            blocklist_info = get_blocklist_info()
            result['blocked'] = True
            result['error'] = {
                'type': 'Blocked URL',
                'message': f'URL is blocked: {matched_domain or "Unknown reason"}'
            }
            log_blocked_request(url, matched_domain or 'unknown', 'redirect_follower')
            return result
        
        current_url = url
        redirect_count = 0
        
        while redirect_count < MAX_REDIRECTS:
            start_time = time.time()
            
            # Make request without following redirects automatically
            response = requests.head(
                current_url,
                headers={'User-Agent': user_agent},
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
                verify=True
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            # Add current step to redirect chain
            step = {
                'url': current_url,
                'status_code': response.status_code,
                'status_text': response.reason,
                'response_time_ms': response_time,
                'location': response.headers.get('Location') if response.status_code in [301, 302, 303, 307, 308] else None
            }
            
            result['redirect_chain'].append(step)
            
            # Check if we have a redirect
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location')
                if not location:
                    result['error'] = {
                        'type': 'Invalid Redirect',
                        'message': f'Redirect status {response.status_code} but no Location header'
                    }
                    break
                
                # Handle relative URLs
                if location.startswith('/'):
                    parsed = urlparse(current_url)
                    current_url = f"{parsed.scheme}://{parsed.netloc}{location}"
                elif not location.startswith(('http://', 'https://')):
                    parsed = urlparse(current_url)
                    current_url = f"{parsed.scheme}://{parsed.netloc}/{location.lstrip('/')}"
                else:
                    current_url = location
                
                redirect_count += 1
            else:
                # No more redirects, this is the final URL
                result['final_url'] = current_url
                result['final_status'] = response.status_code
                break
        
        # Check if we hit the redirect limit
        if redirect_count >= MAX_REDIRECTS:
            result['error'] = {
                'type': 'Too Many Redirects',
                'message': f'Stopped after {MAX_REDIRECTS} redirects to prevent infinite loops'
            }
            result['final_url'] = current_url
            result['final_status'] = response.status_code
        
        result['total_redirects'] = redirect_count
        
    except requests.exceptions.SSLError as e:
        result['error'] = {
            'type': 'SSL Error',
            'message': str(e)
        }
    except requests.exceptions.ConnectionError as e:
        result['error'] = {
            'type': 'Connection Error', 
            'message': str(e)
        }
    except requests.exceptions.Timeout as e:
        result['error'] = {
            'type': 'Timeout Error',
            'message': f'Request timed out after {REQUEST_TIMEOUT} seconds'
        }
    except requests.exceptions.RequestException as e:
        result['error'] = {
            'type': 'Request Error',
            'message': str(e)
        }
    except Exception as e:
        result['error'] = {
            'type': 'Unexpected Error',
            'message': str(e)
        }
    
    return result

@redirect_follower_bp.route('/redirect-follower')
def redirect_follower():
    """Render the redirect follower tool page."""
    increment_click_count('redirect_follower')
    
    json_path = os.path.join(os.path.dirname(__file__), 'redirect_follower_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    current_lang = session.get('lang', 'en')
    
    return render_template('tools/redirect_follower.html', tool_data=tool_data, current_lang=current_lang)

@redirect_follower_bp.route('/api/redirect-follower', methods=['POST'])
def api_redirect_follower():
    """API endpoint to follow redirects for a given URL."""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'error': 'URL is required'
        }), 400
    
    url = data['url'].strip()
    
    # Basic URL validation
    if not url:
        return jsonify({
            'error': 'URL cannot be empty'
        }), 400
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Validate URL format
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return jsonify({
                'error': 'Invalid URL format'
            }), 400
    except Exception:
        return jsonify({
            'error': 'Invalid URL format'
        }), 400
    
    # Follow redirects
    result = follow_redirects(url)
    
    return jsonify(result)
