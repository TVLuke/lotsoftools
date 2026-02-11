from flask import Blueprint, render_template, request, jsonify, session
import requests
import json
import os
from urllib.parse import urlparse
from app.services.link_service import increment_click_count
from app.services.blocklist_service import is_url_blocked, log_blocked_request, get_blocklist_info

website_source_viewer_bp = Blueprint('website_source_viewer', __name__, url_prefix='/tools')

# Request timeout in seconds
REQUEST_TIMEOUT = 10

def get_website_source(url, user_agent='Mozilla/5.0 (compatible; WebsiteSourceViewer/1.0)'):
    """Get the HTML source code of a website."""
    result = {
        'url': url,
        'source_code': None,
        'status_code': None,
        'content_type': None,
        'content_length': None,
        'redirect_count': 0,
        'final_url': url,
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
            log_blocked_request(url, matched_domain or 'unknown', 'website_source_viewer')
            return result
        
        # Make request to get source code
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True
        )
        
        result['status_code'] = response.status_code
        result['content_type'] = response.headers.get('content-type', '')
        result['content_length'] = len(response.content)
        result['final_url'] = response.url
        
        # Count redirects
        if response.history:
            result['redirect_count'] = len(response.history)
        
        # Check if response is HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            result['error'] = {
                'type': 'Not HTML',
                'message': f'Response is not HTML. Content-Type: {content_type}'
            }
            return result
        
        # Get source code
        try:
            # Try to decode with UTF-8 first
            result['source_code'] = response.text
        except UnicodeDecodeError:
            # Fallback to other encodings
            try:
                result['source_code'] = response.content.decode('latin-1')
            except Exception:
                result['source_code'] = response.content.decode('utf-8', errors='replace')
        
    except requests.exceptions.Timeout:
        result['error'] = {
            'type': 'Timeout',
            'message': f'Request timed out after {REQUEST_TIMEOUT} seconds'
        }
    except requests.exceptions.ConnectionError:
        result['error'] = {
            'type': 'Connection Error',
            'message': 'Failed to connect to the website'
        }
    except requests.exceptions.TooManyRedirects:
        result['error'] = {
            'type': 'Too Many Redirects',
            'message': 'Too many redirects detected'
        }
    except requests.exceptions.SSLError as e:
        result['error'] = {
            'type': 'SSL Error',
            'message': f'SSL certificate error: {str(e)}'
        }
    except Exception as e:
        result['error'] = {
            'type': 'Unexpected Error',
            'message': str(e)
        }
    
    return result

@website_source_viewer_bp.route('/website-source-viewer')
def website_source_viewer():
    """Render the website source viewer tool page."""
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'website_source_viewer_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    current_lang = session.get('lang', 'en')
    
    return render_template('tools/website_source_viewer.html', tool_data=tool_data, current_lang=current_lang)

@website_source_viewer_bp.route('/api/website-source-viewer', methods=['POST'])
def api_website_source_viewer():
    """API endpoint to get website source code."""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'error': 'URL is required'
        }), 400
    
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({
            'error': 'URL is required'
        }), 400
    
    # Auto-prepend https:// if no protocol is provided
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
    
    result = get_website_source(url)
    
    return jsonify(result)
