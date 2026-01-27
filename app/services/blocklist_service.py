"""
Blocklist service for URL checker.
Downloads and parses blocklists on startup, checks domains against them.
"""
import json
import os
import logging
from datetime import datetime
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

# Global blocklist storage
_blocked_domains = set()
_blocklist_info = {
    'enabled': False,
    'loaded': False,
    'load_time': None,
    'domain_count': 0,
    'lists_loaded': 0,
    'errors': []
}

# Log file for blocked requests
BLOCKED_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'blocked_requests.log')


def _ensure_log_dir():
    """Ensure the logs directory exists."""
    log_dir = os.path.dirname(BLOCKED_LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)


def load_config():
    """Load blocklist configuration."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'blocklists.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load blocklist config: {e}")
        return {'enabled': False, 'lists': []}


def parse_hosts_file(content):
    """Parse a hosts-format blocklist and extract domains.
    
    Format: 0.0.0.0 domain.com
    Lines starting with # are comments.
    """
    domains = set()
    for line in content.splitlines():
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        # Parse hosts format: 0.0.0.0 domain.com
        parts = line.split()
        if len(parts) >= 2 and parts[0] in ('0.0.0.0', '127.0.0.1'):
            domain = parts[1].lower()
            # Skip localhost entries
            if domain not in ('localhost', 'localhost.localdomain', 'local'):
                domains.add(domain)
    return domains


def download_blocklist(url, timeout=30):
    """Download a blocklist from URL and parse domains."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return parse_hosts_file(response.text)
    except Exception as e:
        logger.error(f"Failed to download blocklist {url}: {e}")
        return set()


def init_blocklists(app=None):
    """Initialize blocklists on application startup.
    
    Downloads all configured blocklists and populates the blocked domains set.
    """
    global _blocked_domains, _blocklist_info
    
    config = load_config()
    _blocklist_info['enabled'] = config.get('enabled', False)
    
    if not _blocklist_info['enabled']:
        print("ℹ Blocklists disabled in configuration")
        _blocklist_info['loaded'] = True
        return
    
    logger.info("Loading blocklists...")
    _ensure_log_dir()
    
    lists = config.get('lists', [])
    errors = []
    total_domains = set()
    lists_loaded = 0
    
    for url in lists:
        logger.info(f"Downloading blocklist: {url}")
        domains = download_blocklist(url)
        if domains:
            total_domains.update(domains)
            lists_loaded += 1
            logger.info(f"  Loaded {len(domains)} domains from {url}")
        else:
            errors.append(f"Failed to load: {url}")
    
    _blocked_domains = total_domains
    _blocklist_info.update({
        'loaded': True,
        'load_time': datetime.now().isoformat(),
        'domain_count': len(total_domains),
        'lists_loaded': lists_loaded,
        'errors': errors
    })
    
    print(f"✓ Blocklists loaded: {len(total_domains):,} domains from {lists_loaded} lists")
    if errors:
        for err in errors:
            print(f"  ⚠ {err}")


def is_domain_blocked(domain):
    """Check if a domain or any of its parent domains is blocked.
    
    Args:
        domain: The domain to check (e.g., 'sub.example.com')
        
    Returns:
        tuple: (is_blocked: bool, matched_domain: str or None)
    """
    if not _blocklist_info['enabled'] or not domain:
        return False, None
    
    domain = domain.lower()
    
    # Check exact match
    if domain in _blocked_domains:
        return True, domain
    
    # Check parent domains (for subdomain blocking)
    parts = domain.split('.')
    for i in range(1, len(parts)):
        parent = '.'.join(parts[i:])
        if parent in _blocked_domains:
            return True, parent
    
    return False, None


def is_url_blocked(url):
    """Check if a URL's domain is blocked.
    
    Args:
        url: Full URL to check
        
    Returns:
        tuple: (is_blocked: bool, matched_domain: str or None)
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc
        # Remove port if present
        if ':' in hostname:
            hostname = hostname.split(':')[0]
        return is_domain_blocked(hostname)
    except Exception:
        return False, None


def log_blocked_request(url, matched_domain, requester_info=None):
    """Log a blocked request to the log file."""
    if not _blocklist_info['enabled']:
        return
    
    try:
        _ensure_log_dir()
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | BLOCKED | {url} | matched: {matched_domain}"
        if requester_info:
            log_entry += f" | from: {requester_info}"
        log_entry += "\n"
        
        with open(BLOCKED_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to log blocked request: {e}")


def get_blocklist_info():
    """Get information about the current blocklist state."""
    return _blocklist_info.copy()


def get_blocked_request_count():
    """Get the count of blocked requests from the log file.
    
    Returns only the count, not any content for privacy.
    """
    try:
        if not os.path.exists(BLOCKED_LOG_FILE):
            return 0
        with open(BLOCKED_LOG_FILE, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0
