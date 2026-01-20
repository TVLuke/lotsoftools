from flask import Blueprint, render_template, request, jsonify
import requests
import json
import os
import ssl
import socket
import time
import hashlib
import re
from datetime import datetime
from urllib.parse import urlparse
from html.parser import HTMLParser
from app.services.link_service import increment_click_count


class MetaTagParser(HTMLParser):
    """Parse HTML to extract meta tags and title."""
    
    def __init__(self):
        super().__init__()
        self.meta_tags = {}
        self.title = None
        self._in_title = False
        self._title_data = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self._in_title = True
            self._title_data = []
        elif tag == 'meta':
            attrs_dict = dict(attrs)
            name = attrs_dict.get('name', attrs_dict.get('property', '')).lower()
            content = attrs_dict.get('content', '')
            if name and content:
                self.meta_tags[name] = content
    
    def handle_data(self, data):
        if self._in_title:
            self._title_data.append(data)
    
    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
            self.title = ''.join(self._title_data).strip()


def extract_meta_tags(html_content):
    """Extract meta tags and title from HTML content."""
    try:
        # Only parse the head section for performance
        head_match = re.search(r'<head[^>]*>(.*?)</head>', html_content, re.IGNORECASE | re.DOTALL)
        html_to_parse = head_match.group(0) if head_match else html_content[:10000]
        
        parser = MetaTagParser()
        parser.feed(html_to_parse)
        
        result = {
            'title': parser.title
        }
        
        # Common meta tags to extract
        important_tags = [
            'description', 'keywords', 'author', 'robots', 'viewport',
            'og:title', 'og:description', 'og:image', 'og:url', 'og:type', 'og:site_name',
            'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image',
            'theme-color', 'generator'
        ]
        
        for tag in important_tags:
            if tag in parser.meta_tags:
                result[tag] = parser.meta_tags[tag]
        
        return result
    except Exception:
        return {}

url_checker_bp = Blueprint('url_checker', __name__, url_prefix='/tools')

# Request timeout in seconds
REQUEST_TIMEOUT = 15

# User agent to use for requests
USER_AGENT = 'Mozilla/5.0 (compatible; LotsOfTools URL Checker/1.0)'

# Cache for URL check results (prevents DOS by rapid repeated requests)
# Format: {cache_key: {'result': ..., 'timestamp': ...}}
_result_cache = {}
CACHE_TTL_SECONDS = 5


def _get_cache_key(url, follow_redirects):
    """Generate a cache key from URL and options."""
    return f"{url}:{follow_redirects}"


def _get_cached_result(url, follow_redirects):
    """Get cached result if still valid, otherwise return None."""
    cache_key = _get_cache_key(url, follow_redirects)
    if cache_key in _result_cache:
        entry = _result_cache[cache_key]
        if time.time() - entry['timestamp'] < CACHE_TTL_SECONDS:
            return entry['result']
        else:
            # Expired, remove it
            del _result_cache[cache_key]
    return None


def _cache_result(url, follow_redirects, result):
    """Cache a result for the URL."""
    cache_key = _get_cache_key(url, follow_redirects)
    _result_cache[cache_key] = {
        'result': result,
        'timestamp': time.time()
    }
    # Clean up old entries occasionally (when cache gets large)
    if len(_result_cache) > 1000:
        _cleanup_cache()


def _cleanup_cache():
    """Remove expired cache entries."""
    now = time.time()
    expired = [k for k, v in _result_cache.items() if now - v['timestamp'] >= CACHE_TTL_SECONDS]
    for k in expired:
        del _result_cache[k]


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
                cipher = ssock.cipher()
                version = ssock.version()
                
                # Parse certificate info - get all fields
                subject = {}
                for item in cert.get('subject', []):
                    for key, value in item:
                        subject[key] = value
                
                issuer = {}
                for item in cert.get('issuer', []):
                    for key, value in item:
                        issuer[key] = value
                
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
                
                # Get all SANs
                sans = [x[1] for x in cert.get('subjectAltName', []) if x[0] == 'DNS']
                
                return {
                    'valid': True,
                    'version': version,
                    'cipher': cipher[0] if cipher else None,
                    'cipher_bits': cipher[2] if cipher else None,
                    'serial_number': cert.get('serialNumber', ''),
                    'subject': {
                        'common_name': subject.get('commonName', ''),
                        'organization': subject.get('organizationName', ''),
                        'organizational_unit': subject.get('organizationalUnitName', ''),
                        'country': subject.get('countryName', ''),
                        'state': subject.get('stateOrProvinceName', ''),
                        'locality': subject.get('localityName', '')
                    },
                    'issuer': {
                        'common_name': issuer.get('commonName', ''),
                        'organization': issuer.get('organizationName', ''),
                        'country': issuer.get('countryName', '')
                    },
                    'not_before': not_before,
                    'not_after': not_after,
                    'days_until_expiry': days_until_expiry,
                    'san': sans[:10],  # First 10 SANs
                    'san_count': len(sans)
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
    
    # Check cache first (prevents DOS by rapid repeated requests)
    cached = _get_cached_result(url, follow_redirects)
    if cached:
        return jsonify(cached)
    
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
        'meta_tags': {},
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
        
        # Collect all response headers
        result['headers'] = dict(response.headers)
        
        # Extract meta tags from HTML content
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type or 'application/xhtml' in content_type:
            try:
                html_content = response.content.decode('utf-8', errors='ignore')
                result['meta_tags'] = extract_meta_tags(html_content)
            except Exception:
                result['meta_tags'] = {}
        else:
            result['meta_tags'] = {}
        
        # Compute content hash (change detection handled in frontend via localStorage)
        content_hash = _compute_content_hash(response.content)
        result['content_hash'] = content_hash[:16]  # Short hash for display
        
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
    
    # Cache the result before returning
    _cache_result(url, follow_redirects, result)
    
    return jsonify(result)
