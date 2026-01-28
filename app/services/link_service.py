import json
import re
import os
import logging
from datetime import datetime
from collections import Counter
from flask import session, request
from app.models.link import Link
from app import db

logger = logging.getLogger(__name__)

# Log file for user agent tracking (in data/ for Docker volume persistence)
UA_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'user_agents.log')
# Log file for referrer tracking
REFERRER_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'referrers.log')

# Server start time for stats display
_server_start_time = datetime.now()

def get_server_start_time():
    """Get the server start time."""
    return _server_start_time


def get_ua_log_file_size():
    """Get the size of the user agent log file in human-readable format."""
    try:
        if os.path.exists(UA_LOG_FILE):
            size_bytes = os.path.getsize(UA_LOG_FILE)
            # Convert to human-readable
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.1f} TB"
        return "0 B"
    except Exception:
        return "unknown"

# Load bot patterns from well-known-bots.json for User-Agent detection
_bot_regex_patterns = []
_bot_simple_patterns = [
    'bot', 'crawler', 'spider', 'slurp', 'wget', 'curl', 'python-requests',
    'python-urllib', 'java/', 'libwww', 'httpclient', 'go-http-client',
    'scrapy', 'nutch', 'headlesschrome', 'phantomjs', 'prerender',
    'lighthouse', 'pagespeed', 'gtmetrix', 'playwright', 'claudebot', 'req/',
    'python-requests/'
]

def _ensure_log_dir():
    """Ensure the logs directory exists."""
    log_dir = os.path.dirname(UA_LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)


def _parse_ua_log():
    """Parse user agent log file and return aggregated stats.
    
    Log format: timestamp|BOT/HUMAN|url|user_agent
    Returns dict: {user_agent: {'count': N, 'is_bot': bool}}
    """
    stats = {}
    try:
        if not os.path.exists(UA_LOG_FILE):
            return stats
        with open(UA_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                parts = line.split('|')
                # Format: timestamp|BOT/HUMAN|url|user_agent (4 parts)
                # Old format: timestamp|BOT/HUMAN|user_agent (3 parts)
                if len(parts) >= 4:
                    is_bot = parts[1].strip() == 'BOT'
                    ua = parts[3].strip()
                elif len(parts) >= 3:
                    is_bot = parts[1].strip() == 'BOT'
                    ua = parts[2].strip()
                else:
                    continue
                if ua in stats:
                    stats[ua]['count'] += 1
                else:
                    stats[ua] = {'count': 1, 'is_bot': is_bot}
    except Exception as e:
        logger.error(f"Failed to parse UA log: {e}")
    return stats


def get_user_agent_stats():
    """Get user agent statistics sorted by count descending."""
    stats = _parse_ua_log()
    return sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)


def get_bot_user_agents():
    """Get only bot user agents sorted by count descending."""
    stats = _parse_ua_log()
    # UAs seen as human - used to filter behavioral detection false positives
    human_uas = {ua for ua, data in stats.items() if not data['is_bot']}
    bots = []
    for ua, data in stats.items():
        if data['is_bot']:
            # Skip behavioral detection false positives (same UA also seen as human)
            if _categorize_user_agent(ua) == 'Behavioral Detection' and ua in human_uas:
                continue
            bots.append((ua, data))
    return sorted(bots, key=lambda x: x[1]['count'], reverse=True)


def _categorize_user_agent(user_agent):
    """Categorize a user agent string by company/type.
    
    Only includes bots we've actually observed in logs.
    Categories are dynamic - add new ones as they appear.
    """
    ua_lower = user_agent.lower()
    
    # OpenAI bots (GPTBot, ChatGPT-User, OAI-SearchBot)
    if 'gptbot' in ua_lower or 'chatgpt' in ua_lower or 'oai-searchbot' in ua_lower or 'openai.com' in ua_lower:
        return 'OpenAI'
    # Anthropic (ClaudeBot)
    if 'claudebot' in ua_lower or 'anthropic' in ua_lower:
        return 'Anthropic'
    # Google (Googlebot)
    if 'googlebot' in ua_lower or 'google.com/bot' in ua_lower:
        return 'Google'
    # air.ai
    if 'air.ai' in ua_lower:
        return 'air.ai'
    # PetalBot (Huawei search)
    if 'petalbot' in ua_lower:
        return 'Huawei'
    # UptimeRobot (monitoring)
    if 'uptimerobot' in ua_lower:
        return 'UptimeRobot'
    # Python urllib (scripts/bots)
    if 'python-urllib' in ua_lower:
        return 'Python'
    # Amazon (Amazonbot)
    if 'amazonbot' in ua_lower:
        return 'Amazon'
    # Let's Encrypt (validation)
    if 'letsencrypt' in ua_lower:
        return "Let's Encrypt"
    # LeakIX (security scanner)
    if 'leakix' in ua_lower:
        return 'LeakIX'
    # Censys (security scanner)
    if 'censys' in ua_lower:
        return 'Censys'
    # Go HTTP client
    if 'go-http-client' in ua_lower:
        return 'Go'
    # OkHttp (Java/Kotlin)
    if 'okhttp' in ua_lower:
        return 'OkHttp'
    # HeadlessChrome (automation)
    if 'headlesschrome' in ua_lower:
        return 'HeadlessChrome'
    # Generic other bots (matched by UA pattern)
    if any(p in ua_lower for p in _bot_simple_patterns):
        return 'Other Bots'
    
    # Caught by behavioral detection only (no cookies/Accept-Language)
    return 'Behavioral Detection'


def get_user_agent_stats_by_company():
    """Get user agent statistics aggregated by company."""
    stats = _parse_ua_log()
    company_stats = {}
    
    # Collect all UAs that have been seen as human
    human_uas = {ua for ua, data in stats.items() if not data['is_bot']}
    
    for ua, data in stats.items():
        if data['is_bot']:
            company = _categorize_user_agent(ua)
            # If this UA was also seen as human, it's likely human (behavioral false positive)
            if company == 'Behavioral Detection' and ua in human_uas:
                company = 'Humans'
        else:
            company = 'Humans'
        
        if company in company_stats:
            company_stats[company] += data['count']
        else:
            company_stats[company] = data['count']
    
    return company_stats


def get_human_user_agents():
    """Get only human user agents sorted by count descending."""
    stats = _parse_ua_log()
    # UAs seen as human
    human_uas = {ua for ua, data in stats.items() if not data['is_bot']}
    humans = []
    for ua, data in stats.items():
        if not data['is_bot']:
            humans.append((ua, data))
        elif _categorize_user_agent(ua) == 'Behavioral Detection' and ua in human_uas:
            # Include behavioral detection false positives (same UA also seen as human)
            humans.append((ua, data))
    return sorted(humans, key=lambda x: x[1]['count'], reverse=True)


def track_user_agent(user_agent, is_bot, url=None):
    """Log user agent to file for persistent tracking."""
    try:
        _ensure_log_dir()
        timestamp = datetime.now().isoformat()
        bot_label = 'BOT' if is_bot else 'HUMAN'
        # Sanitize user agent (remove newlines, limit length)
        ua_clean = user_agent.replace('\n', ' ').replace('|', ' ')[:500]
        url_clean = (url or '').replace('|', ' ')[:100]
        log_entry = f"{timestamp}|{bot_label}|{url_clean}|{ua_clean}\n"
        
        with open(UA_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to log user agent: {e}")


def track_referrer(referrer, is_bot, url=None):
    """Log referrer to file for persistent tracking."""
    if not referrer:
        return
    try:
        _ensure_log_dir()
        timestamp = datetime.now().isoformat()
        bot_label = 'BOT' if is_bot else 'HUMAN'
        # Sanitize referrer (remove newlines, limit length)
        ref_clean = referrer.replace('\n', ' ').replace('|', ' ')[:500]
        url_clean = (url or '').replace('|', ' ')[:100]
        log_entry = f"{timestamp}|{bot_label}|{url_clean}|{ref_clean}\n"
        
        with open(REFERRER_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to log referrer: {e}")


def _parse_referrer_log():
    """Parse referrer log file and return aggregated stats.
    
    Log format: timestamp|BOT/HUMAN|url|referrer
    Returns dict: {referrer: {'count': N, 'is_bot': bool}}
    """
    stats = {}
    try:
        if not os.path.exists(REFERRER_LOG_FILE):
            return stats
        with open(REFERRER_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    is_bot = parts[1].strip() == 'BOT'
                    referrer = parts[3].strip()
                    if referrer in stats:
                        stats[referrer]['count'] += 1
                    else:
                        stats[referrer] = {'count': 1, 'is_bot': is_bot}
    except Exception as e:
        logger.error(f"Failed to parse referrer log: {e}")
    return stats


def _extract_referrer_domain(referrer):
    """Extract domain from referrer URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(referrer)
        return parsed.netloc or referrer
    except:
        return referrer


def get_referrer_stats():
    """Get referrer statistics sorted by count descending."""
    stats = _parse_referrer_log()
    return sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)


def get_referrer_stats_by_domain():
    """Get referrer statistics aggregated by domain."""
    stats = _parse_referrer_log()
    domain_stats = {}
    
    for referrer, data in stats.items():
        if not data['is_bot']:  # Only count human referrers
            domain = _extract_referrer_domain(referrer)
            if domain in domain_stats:
                domain_stats[domain] += data['count']
            else:
                domain_stats[domain] = data['count']
    
    return domain_stats


def _load_bot_patterns():
    """Load regex patterns from well-known-bots.json"""
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

def is_bot_request():
    """Check if the current request is from a bot/crawler based on User-Agent and behavior."""
    _load_bot_patterns()
    
    user_agent = request.headers.get('User-Agent', '')
    user_agent_lower = user_agent.lower()
    
    # No User-Agent is suspicious
    if not user_agent:
        return True
    
    # Check against simple patterns (fast)
    for pattern in _bot_simple_patterns:
        if pattern in user_agent_lower:
            return True
    
    # Check against regex patterns from well-known-bots.json
    for regex in _bot_regex_patterns:
        if regex.search(user_agent):
            return True
    
    # Behavioral check: real browsers have cookies after first visit
    # A bot making many requests without cookies is suspicious
    has_cookies = bool(request.cookies)
    has_accept_language = bool(request.headers.get('Accept-Language', ''))
    
    # If user agent looks like a browser but has NO cookies and NO accept-language,
    # it's likely a bot pretending to be a browser
    if not has_cookies and not has_accept_language:
        return True
    
    return False

def get_all_links():
    return Link.query.all()

def get_link_by_url(url):
    return Link.query.filter_by(url=url).first()

def increment_click_count(url):
    """Increment the click count for a link by its URL. Separates bot vs human clicks, theme, and language."""
    link = get_link_by_url(url)
    if link:
        user_agent = request.headers.get('User-Agent', '')
        referrer = request.headers.get('Referer', '')
        is_bot = is_bot_request()
        track_user_agent(user_agent, is_bot, url)
        track_referrer(referrer, is_bot, url)
        # Track country
        from app.services.country_block import get_client_ip, get_country_code, track_country
        ip = get_client_ip()
        country = get_country_code(ip)
        track_country(country, is_bot, url)
        if is_bot:
            link.bot_click_count = (link.bot_click_count or 0) + 1
        else:
            link.click_count = (link.click_count or 0) + 1
            
            # Track theme from cookie (only for humans)
            theme = request.cookies.get('lotsoftools_theme', '')
            if theme == 'light':
                link.light_clicks = (link.light_clicks or 0) + 1
            elif theme == 'dark':
                link.dark_clicks = (link.dark_clicks or 0) + 1
            elif theme == 'high-contrast':
                link.high_contrast_clicks = (link.high_contrast_clicks or 0) + 1
            else:
                link.system_theme_clicks = (link.system_theme_clicks or 0) + 1
            
            # Track language from session (only for humans)
            lang = session.get('lang', 'en')
            if lang == 'en':
                link.en_clicks = (link.en_clicks or 0) + 1
            elif lang == 'de':
                link.de_clicks = (link.de_clicks or 0) + 1
        
        db.session.commit()
        return True
    return False


def track_bandwidth(url, bytes_count, is_bot):
    """Track bandwidth served for a link."""
    link = get_link_by_url(url)
    if link:
        if is_bot:
            link.bot_bytes_served = (link.bot_bytes_served or 0) + bytes_count
        else:
            link.bytes_served = (link.bytes_served or 0) + bytes_count
        db.session.commit()
        return True
    return False


def get_links_stats():
    """Get all links with stats, ordered by click count descending."""
    links = Link.query.order_by(Link.click_count.desc()).all()
    return [{
        'name': link.name, 
        'url': link.url, 
        'click_count': link.click_count or 0, 
        'bot_click_count': link.bot_click_count or 0,
        'light_clicks': link.light_clicks or 0,
        'dark_clicks': link.dark_clicks or 0,
        'high_contrast_clicks': link.high_contrast_clicks or 0,
        'system_theme_clicks': link.system_theme_clicks or 0,
        'en_clicks': link.en_clicks or 0,
        'de_clicks': link.de_clicks or 0,
        'bytes_served': link.bytes_served or 0,
        'bot_bytes_served': link.bot_bytes_served or 0,
        'is_meta_link': link.is_meta_link or False
    } for link in links]

def get_theme_language_totals():
    """Get total counts for theme and language across all links."""
    links = Link.query.all()
    light = sum(link.light_clicks or 0 for link in links)
    dark = sum(link.dark_clicks or 0 for link in links)
    high_contrast = sum(link.high_contrast_clicks or 0 for link in links)
    system_theme = sum(link.system_theme_clicks or 0 for link in links)
    total_theme = light + dark + high_contrast + system_theme
    totals = {
        'light': light,
        'dark': dark,
        'high_contrast': high_contrast,
        'system_theme': system_theme,
        'system_theme_pct': round(system_theme / total_theme * 100, 1) if total_theme > 0 else 0,
        'en': sum(link.en_clicks or 0 for link in links),
        'de': sum(link.de_clicks or 0 for link in links)
    }
    return totals

def get_links_by_category(lang=None):
    if lang is None:
        lang = session.get('lang', 'en')
    
    links = get_all_links()
    categories = {}
    
    for link in links:
        link_dict = link.to_dict(lang)
        for tag in link.tags:
            if tag not in categories:
                categories[tag] = []
            categories[tag].append(link_dict)
    
    sorted_categories = dict(sorted(categories.items()))
    
    for category in sorted_categories:
        sorted_categories[category].sort(key=lambda x: x.get('name', '').lower())
    
    return sorted_categories


def get_related_tools(current_url, limit=4, lang=None):
    """Get related tools based on shared tags, excluding current tool."""
    if lang is None:
        lang = session.get('lang', 'en')
    
    # Try exact match first, then try base path (for tools with dynamic segments like /tools/color/HEXCODE)
    current_link = get_link_by_url(current_url)
    if not current_link:
        # Try matching by prefix - find tool whose route is a prefix of current_url
        all_links = get_all_links()
        for link in all_links:
            if current_url.startswith(link.url) and link.url != '/':
                current_link = link
                break
    
    if not current_link or not current_link.tags:
        return []
    
    current_tags = set(current_link.tags)
    all_links = get_all_links()
    
    # Score links by number of shared tags
    scored_links = []
    for link in all_links:
        if link.url == current_link.url:
            continue
        shared_tags = len(current_tags & set(link.tags))
        if shared_tags > 0:
            scored_links.append((shared_tags, link))
    
    # Sort by score (descending), then by name
    scored_links.sort(key=lambda x: (-x[0], x[1].get_name(lang).lower()))
    
    # Return top N as dicts
    return [link.to_dict(lang) for _, link in scored_links[:limit]]
