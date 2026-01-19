from flask import Blueprint, render_template, request, jsonify
import requests
import json
import os
import ssl
import socket
import time
import hashlib
import threading
from datetime import datetime, timedelta
from urllib.parse import urlparse
from app.services.link_service import increment_click_count

url_checker_bp = Blueprint('url_checker', __name__, url_prefix='/tools')

# Request timeout in seconds
REQUEST_TIMEOUT = 15

# User agent to use for requests
USER_AGENT = 'Mozilla/5.0 (compatible; LotsOfTools URL Checker/1.0)'

# In-memory storage for content hashes (URL -> list of {hash, timestamp})
# Only keeps hashes from the last hour
_content_hashes = {}
_hash_lock = threading.Lock()
HASH_RETENTION_HOURS = 1


def _cleanup_old_hashes():
    """Remove hashes older than HASH_RETENTION_HOURS."""
    cutoff = datetime.now() - timedelta(hours=HASH_RETENTION_HOURS)
    with _hash_lock:
        urls_to_remove = []
        for url, entries in _content_hashes.items():
            # Filter out old entries
            _content_hashes[url] = [e for e in entries if e['timestamp'] > cutoff]
            # Mark empty URLs for removal
            if not _content_hashes[url]:
                urls_to_remove.append(url)
        for url in urls_to_remove:
            del _content_hashes[url]


def _store_hash(url, content_hash):
    """Store a content hash for a URL."""
    _cleanup_old_hashes()
    with _hash_lock:
        if url not in _content_hashes:
            _content_hashes[url] = []
        _content_hashes[url].append({
            'hash': content_hash,
            'timestamp': datetime.now()
        })


def _get_previous_hashes(url):
    """Get previous hashes for a URL (excluding the most recent one just added)."""
    _cleanup_old_hashes()
    with _hash_lock:
        entries = _content_hashes.get(url, [])
        # Return all but potentially the last one (which might be current)
        return entries[:-1] if len(entries) > 1 else []


def _compute_content_hash(content):
    """Compute SHA-256 hash of content."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()

@url_checker_bp.route('/url-checker')
def index():
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'url_checker_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/url_checker.html', tool_data=tool_data)


def validate_url(url):
    """Validate that URL is well-formed and uses HTTPS."""
    if not url:
        return False, "URL is required"
    
    # Must start with https://
    if not url.startswith('https://'):
        return False, "URL must use HTTPS"
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "Invalid URL format"
        # Basic check for valid domain
        if '.' not in parsed.netloc and parsed.netloc != 'localhost':
            return False, "Invalid domain"
        return True, None
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def get_ssl_info(hostname, port=443):
    """Get SSL certificate information for a hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Parse certificate info
                subject = dict(x[0] for x in cert.get('subject', []))
                issuer = dict(x[0] for x in cert.get('issuer', []))
                
                # Parse dates
                not_before = cert.get('notBefore', '')
                not_after = cert.get('notAfter', '')
                
                # Convert to datetime if possible
                try:
                    not_before_dt = datetime.strptime(not_before, '%b %d %H:%M:%S %Y %Z')
                    not_after_dt = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after_dt - datetime.utcnow()).days
                except:
                    days_until_expiry = None
                
                return {
                    'valid': True,
                    'subject': subject.get('commonName', 'Unknown'),
                    'issuer': issuer.get('organizationName', issuer.get('commonName', 'Unknown')),
                    'not_before': not_before,
                    'not_after': not_after,
                    'days_until_expiry': days_until_expiry,
                    'san': [x[1] for x in cert.get('subjectAltName', []) if x[0] == 'DNS'][:5]  # First 5 SANs
                }
    except ssl.SSLCertVerificationError as e:
        return {
            'valid': False,
            'error': 'Certificate verification failed',
            'message': str(e)
        }
    except Exception as e:
        return {
            'valid': False,
            'error': 'SSL connection failed',
            'message': str(e)
        }


@url_checker_bp.route('/url-checker/check', methods=['POST'])
def check_url():
    data = request.get_json()
    url = data.get('url', '').strip()
    follow_redirects = data.get('follow_redirects', True)
    
    # Validate URL
    is_valid, error_msg = validate_url(url)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    parsed = urlparse(url)
    hostname = parsed.netloc
    if ':' in hostname:
        hostname = hostname.split(':')[0]
    
    result = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'reachable': False,
        'status_code': None,
        'status_text': None,
        'response_time_ms': None,
        'final_url': None,
        'redirects': [],
        'headers': {},
        'ssl': None,
        'content_hash': None,
        'content_changed': None,
        'previous_checks': 0,
        'error': None
    }
    
    # Get SSL info first
    try:
        result['ssl'] = get_ssl_info(hostname)
    except Exception as e:
        result['ssl'] = {'valid': False, 'error': str(e)}
    
    # Make HTTP request
    try:
        start_time = time.time()
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # Track redirects manually if needed
        if follow_redirects:
            response = requests.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
                verify=True
            )
            
            # Collect redirect history
            for r in response.history:
                result['redirects'].append({
                    'url': r.url,
                    'status_code': r.status_code,
                    'status_text': r.reason
                })
            
            result['final_url'] = response.url
        else:
            response = requests.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
                verify=True
            )
            result['final_url'] = url
        
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        result['reachable'] = True
        result['status_code'] = response.status_code
        result['status_text'] = response.reason
        result['response_time_ms'] = response_time_ms
        
        # Collect relevant headers
        headers_to_collect = [
            'Server', 'Content-Type', 'Content-Length', 'Cache-Control',
            'X-Powered-By', 'X-Frame-Options', 'X-Content-Type-Options',
            'Strict-Transport-Security', 'Content-Security-Policy',
            'X-XSS-Protection', 'Referrer-Policy', 'Permissions-Policy'
        ]
        
        for header in headers_to_collect:
            if header in response.headers:
                result['headers'][header] = response.headers[header]
        
        # Compute content hash and detect changes
        content_hash = _compute_content_hash(response.content)
        result['content_hash'] = content_hash[:16]  # Short hash for display
        
        # Get previous hashes before storing new one
        check_url_key = result['final_url'] or url
        previous = _get_previous_hashes(check_url_key)
        result['previous_checks'] = len(previous)
        
        if previous:
            # Check if content changed from any previous hash
            previous_hashes = [e['hash'] for e in previous]
            if content_hash in previous_hashes:
                result['content_changed'] = False
            else:
                result['content_changed'] = True
        
        # Store the new hash
        _store_hash(check_url_key, content_hash)
        
    except requests.exceptions.SSLError as e:
        result['error'] = {
            'type': 'SSL Error',
            'message': str(e)
        }
    except requests.exceptions.ConnectionError as e:
        result['error'] = {
            'type': 'Connection Error',
            'message': 'Could not connect to the server'
        }
    except requests.exceptions.Timeout as e:
        result['error'] = {
            'type': 'Timeout',
            'message': f'Request timed out after {REQUEST_TIMEOUT} seconds'
        }
    except requests.exceptions.TooManyRedirects as e:
        result['error'] = {
            'type': 'Too Many Redirects',
            'message': 'Too many redirects detected'
        }
    except Exception as e:
        result['error'] = {
            'type': 'Error',
            'message': str(e)
        }
    
    return jsonify(result)
