"""Bot detection utilities extracted from link_service.py for testing."""

import os
import re
import json
from flask import request

# Log file paths (defined here to avoid circular imports)
HONEYPOT_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'honeypot.log')
JS_CAPABLE_LOG_FILE = 'logs/js_capable_users.log'

# Reason suffixes for definitive bot detection (cannot be overridden by human)
REASON_OLD_CHROME = "(old Chrome)"
REASON_OLD_FIREFOX = "(old Firefox)"
REASON_OLD_IOS = "(old iOS)"
REASON_OLD_WINDOWS = "(old Windows)"
REASON_OLD_BROWSER = "(old browser)"
REASON_VERY_OLD_OS = "(very old OS)"
REASON_BOT_PATTERN = "Bot pattern:"
REASON_KNOWN_BOT = "Known bot pattern"
REASON_HONEYPOT = "Honeypot link access"
REASON_SUBDOMAIN_REFERER = "subdomain referer (bot)"
REASON_IP_REFERER = "IP address referer (bot)"

# Tuple of all definitive reasons for easy checking
DEFINITIVE_BOT_REASONS = (
    REASON_OLD_CHROME, REASON_OLD_FIREFOX, REASON_OLD_IOS,
    REASON_OLD_WINDOWS, REASON_OLD_BROWSER, REASON_VERY_OLD_OS, REASON_BOT_PATTERN,
    REASON_KNOWN_BOT, REASON_HONEYPOT, REASON_SUBDOMAIN_REFERER, REASON_IP_REFERER
)

# Load bot patterns from well-known-bots.json for User-Agent detection
_bot_regex_patterns = []
_bot_simple_patterns = [
    'bot', 'crawler', 'spider', 'slurp', 'wget', 'curl', 'python-requests',
    'python-urllib', 'java/', 'libwww', 'httpclient', 'go-http-client',
    'scrapy', 'nutch', 'headlesschrome', 'phantomjs', 'prerender',
    'lighthouse', 'pagespeed', 'gtmetrix', 'playwright', 'claudebot', 'req/',
    'python-requests/', 'lotsoftools_url_checker', 'leakix', 'letsencrypt', 'petalbot',
    'ct-monitor/', 'youruseragenthere'
]

def _load_bot_patterns():
    """Load bot patterns from well-known-bots.json file."""
    global _bot_regex_patterns
    if _bot_regex_patterns:
        return
    
    json_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'well-known-bots-main', 'well-known-bots.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            bots = json.load(f)
            for bot in bots:
                patterns = bot.get('pattern', {}).get('accepted', [])
                for pattern in patterns:
                    try:
                        _bot_regex_patterns.append(re.compile(pattern, re.IGNORECASE))
                    except re.error:
                        pass
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def _log_honeypot_access(user_agent):
    """Log honeypot access to a file."""
    os.makedirs(os.path.dirname(HONEYPOT_LOG_FILE), exist_ok=True)
    with open(HONEYPOT_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{user_agent}\n")

def is_bot_request():
    """Check if the current request is from a bot/crawler based on User-Agent and behavior."""
    _load_bot_patterns()
    
    # Check if this is the bot-policy honeypot page
    if request.path and request.path == '/bot-policy':
        # Log to honeypot log file
        _log_honeypot_access(request.headers.get('User-Agent', ''))
        return True, REASON_HONEYPOT
    
    user_agent = request.headers.get('User-Agent', '')
    if not user_agent:
        return True, "No User-Agent header"
    
    user_agent_lower = user_agent.lower()
    
    # Specific Edge 12.246 UA - always bot
    if 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/42.0.2311.135 safari/537.36 edge/12.246' in user_agent_lower:
        return True, f"Edge 12.246 {REASON_OLD_BROWSER}"
    
    # Specific Firefox bot UAs - known scraper signatures
    if 'mozilla/5.0 (x11; ubuntu; linux x86_64; rv:109.0) gecko/20100101 firefox/117.0' in user_agent_lower:
        return True, f"Firefox 117 {REASON_OLD_FIREFOX}"
    if 'mozilla/5.0 (x11; linux i686; rv:109.0) gecko/20100101 firefox/120.0' in user_agent_lower:
        return True, f"Firefox 120 {REASON_OLD_FIREFOX}"
    
    # Chrome versions below 90 are old (4+ years) - likely bots
    chrome_match = re.search(r'chrome/(\d+)\.', user_agent_lower)
    if chrome_match and int(chrome_match.group(1)) < 90:
        return True, f"Chrome {chrome_match.group(1)} {REASON_OLD_CHROME}"
    
    # iOS versions below 14 are old (5+ years) - likely bots
    ios_match = re.search(r'cpu iphone os (\d+)_(\d+)(?:_(\d+))?', user_agent_lower)
    if ios_match and int(ios_match.group(1)) < 14:
        minor = ios_match.group(2)
        patch = ios_match.group(3) if ios_match.group(3) else ''
        version = f"ios {ios_match.group(1)}.{minor}"
        if patch:
            version += f".{patch}"
        return True, f"{version} {REASON_OLD_IOS}"
    
    # Firefox versions below 100 are old (4+ years) - likely bots
    firefox_match = re.search(r'firefox/(\d+)', user_agent_lower)
    if firefox_match and int(firefox_match.group(1)) < 100:
        return True, f"Firefox {firefox_match.group(1)} {REASON_OLD_FIREFOX}"
    
    # Windows NT versions below 10 are old (Windows 7/8/8.1 from 2009-2013)
    windows_match = re.search(r'windows nt (\d+\.\d+)', user_agent_lower)
    if windows_match:
        major_version = float(windows_match.group(1))
        if major_version < 10.0:
            return True, f"Windows NT {windows_match.group(1)} {REASON_OLD_WINDOWS}"
    
    # Windows XP/2000 etc. are very old
    if 'windows xp' in user_agent_lower or 'windows 2000' in user_agent_lower:
        return True, f"Windows XP/2000 {REASON_VERY_OLD_OS}"
    
    # Check for lotsof.tools subdomains in referer (no subdomains exist)
    referer = request.headers.get('Referer', '').lower()
    if referer and ('lotsof.tools' in referer and not referer.startswith('https://lotsof.tools') and not referer.startswith('http://lotsof.tools')):
        return True, f"lotsof.tools {REASON_SUBDOMAIN_REFERER}"
    
    # Check for IP addresses in referer (IPv4 space crawlers)
    if referer:
        # Match IP with optional port (e.g., 152.53.202.205 or 152.53.202.205:80)
        ip_pattern = r'^https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?/'
        if re.match(ip_pattern, referer):
            return True, REASON_IP_REFERER
    
    # Check against simple patterns (fast)
    for pattern in _bot_simple_patterns:
        if pattern in user_agent_lower:
            return True, f"{REASON_BOT_PATTERN} {pattern}"
    
    # Check against regex patterns from well-known-bots.json
    for regex in _bot_regex_patterns:
        if regex.search(user_agent):
            return True, REASON_KNOWN_BOT
    
    # Behavioral check: real browsers have cookies and Accept-Language
    # A bot making many requests without these headers is suspicious
    has_cookies = bool(request.cookies)
    has_accept_language = bool(request.headers.get('Accept-Language', ''))
    
    # If user agent looks like a browser but has NO cookies and NO accept-language,
    # it's likely a bot pretending to be a browser
    if not has_cookies and not has_accept_language:
        return True, "No cookies or Accept-Language"
    
    # If user agent looks like a browser but has NO Accept-Language header,
    # it's likely a bot (real browsers always send Accept-Language)
    if not has_accept_language:
        return True, "No Accept-Language header"
    
    return False, "Human"

def is_js_capable_user(user_agent):
    """Check if this user agent has been verified as JavaScript-capable.
    
    If a user agent has executed JavaScript and accepted cookies,
    it's very likely human even if other signals suggest bot.
    """
    try:
        if not os.path.exists(JS_CAPABLE_LOG_FILE):
            return False
        
        # Look for recent entries (last 7 days) with this user agent
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(days=7)
        
        with open(JS_CAPABLE_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 4:
                    timestamp_str = parts[0]
                    bot_detection = parts[1]
                    logged_ua = parts[3]
                    
                    # Check if user agent matches (allowing for minor variations)
                    if logged_ua in user_agent or user_agent in logged_ua:
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if timestamp > cutoff_time:
                                # Found recent JavaScript-capable activity
                                return True
                        except ValueError:
                            # Skip malformed timestamps
                            continue
        
        return False
    except Exception:
        # If we can't check logs, assume not JS-capable
        return False

def enhanced_bot_detection():
    """Enhanced bot detection that considers JavaScript capability."""
    # First, run standard bot detection
    is_bot, reason = is_bot_request()
    
    # If detected as bot, check if this UA has been verified as JavaScript-capable
    if is_bot:
        user_agent = request.headers.get('User-Agent', '')
        if is_js_capable_user(user_agent):
            # Override bot detection - JavaScript execution + cookies = likely human
            return False, f"Human (JS-capable, was: {reason})"
    
    return is_bot, reason
