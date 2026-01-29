"""Bot detection utilities extracted from link_service.py for testing."""

import os
import re
import json
from flask import request

# Load bot patterns from well-known-bots.json for User-Agent detection
_bot_regex_patterns = []
_bot_simple_patterns = [
    'bot', 'crawler', 'spider', 'slurp', 'wget', 'curl', 'python-requests',
    'python-urllib', 'java/', 'libwww', 'httpclient', 'go-http-client',
    'scrapy', 'nutch', 'headlesschrome', 'phantomjs', 'prerender',
    'lighthouse', 'pagespeed', 'gtmetrix', 'playwright', 'claudebot', 'req/',
    'python-requests/', 'lotsoftools_url_checker'
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
    log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'honeypot.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{user_agent}\n")

def is_bot_request():
    """Check if the current request is from a bot/crawler based on User-Agent and behavior."""
    _load_bot_patterns()
    
    # Check if this is the bot-policy honeypot page
    if request.path and request.path == '/bot-policy':
        # Log to honeypot log file
        _log_honeypot_access(request.headers.get('User-Agent', ''))
        return True, "Honeypot link access"
    
    user_agent = request.headers.get('User-Agent', '')
    if not user_agent:
        return True, "No User-Agent header"
    
    user_agent_lower = user_agent.lower()
    
    # Specific Edge 12.246 UA - always bot
    if 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/42.0.2311.135 safari/537.36 edge/12.246' in user_agent_lower:
        return True, "Edge 12.246 (old browser)"
    
    # Chrome versions below 90 are old (4+ years) - likely bots
    chrome_match = re.search(r'chrome/(\d+)\.', user_agent_lower)
    if chrome_match and int(chrome_match.group(1)) < 90:
        return True, f"Chrome {chrome_match.group(1)} (old Chrome)"
    
    # iOS versions below 14 are old (5+ years) - likely bots
    ios_match = re.search(r'cpu iphone os (\d+)_(\d+)(?:_(\d+))?', user_agent_lower)
    if ios_match and int(ios_match.group(1)) < 14:
        minor = ios_match.group(2)
        patch = ios_match.group(3) if ios_match.group(3) else ''
        version = f"ios {ios_match.group(1)}.{minor}"
        if patch:
            version += f".{patch}"
        return True, f"{version} (old iOS)"
    
    # Android versions below 11 are old (5+ years) - likely bots
    android_match = re.search(r'android (\d+)', user_agent_lower)
    if android_match and int(android_match.group(1)) < 11:
        return True, f"Android {android_match.group(1)} (old Android)"
    
    # Firefox versions below 100 are old (3+ years) - likely bots
    firefox_match = re.search(r'firefox/(\d+)', user_agent_lower)
    if firefox_match and int(firefox_match.group(1)) < 100:
        return True, f"Firefox {firefox_match.group(1)} (old Firefox)"
    
    # Windows NT versions below 10 are old (Windows 7/8/8.1 from 2009-2013)
    windows_match = re.search(r'windows nt (\d+\.\d+)', user_agent_lower)
    if windows_match:
        major_version = float(windows_match.group(1))
        if major_version < 10.0:
            return True, f"Windows NT {windows_match.group(1)} (old Windows)"
    
    # Windows XP/2000 etc. are very old
    if 'windows xp' in user_agent_lower or 'windows 2000' in user_agent_lower:
        return True, "Windows XP/2000 (very old OS)"
    
    # Check for lotsof.tools subdomains in referer (no subdomains exist)
    referer = request.headers.get('Referer', '').lower()
    if referer and ('lotsof.tools' in referer and not referer.startswith('https://lotsof.tools') and not referer.startswith('http://lotsof.tools')):
        return True, "lotsof.tools subdomain referer (bot)"
    
    # Check for IP addresses in referer (IPv4 space crawlers)
    if referer:
        import re
        # Match IP with optional port (e.g., 152.53.202.205 or 152.53.202.205:80)
        ip_pattern = r'^https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?/'
        if re.match(ip_pattern, referer):
            return True, "IP address referer (bot)"
    
    # Check against simple patterns (fast)
    for pattern in _bot_simple_patterns:
        if pattern in user_agent_lower:
            return True, f"Bot pattern: {pattern}"
    
    # Check against regex patterns from well-known-bots.json
    for regex in _bot_regex_patterns:
        if regex.search(user_agent):
            return True, "Known bot pattern"
    
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
