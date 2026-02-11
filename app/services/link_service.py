import os
import json
import logging
from datetime import datetime
from collections import Counter
from flask import session, request
from app.routes.cookie_consent import JS_CAPABLE_LOG_FILE
from app.services.bot_detection import HONEYPOT_LOG_FILE
from app.services.blocklist_service import BLOCKED_LOG_FILE
from app.models.link import Link
from app import db

logger = logging.getLogger(__name__)

# Log file for user agent tracking (in data/ for Docker volume persistence)
UA_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'user_agents.log')
# Log file for referrer tracking
REFERRER_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'referrers.log')
# Log file for Accept-Language tracking (humans only)
ACCEPT_LANG_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'accept_languages.log')

# Log rotation settings
MAX_LOG_ENTRIES = 3_000_000

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

def get_all_log_file_sizes():
    """Get sizes of all log files in the system."""
    log_files = []
    
    # Define all log file paths
    log_paths = [
        ('User Agents', UA_LOG_FILE),
        ('Referrers', REFERRER_LOG_FILE),
        ('Accept Languages', ACCEPT_LANG_LOG_FILE),
        ('Blocked Requests', BLOCKED_LOG_FILE),
        ('JS-Capable Users', JS_CAPABLE_LOG_FILE),
        ('Honeypot', HONEYPOT_LOG_FILE),
    ]
    
    for name, path in log_paths:
        try:
            if os.path.exists(path):
                size_bytes = os.path.getsize(path)
                # Convert to human-readable
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size_bytes < 1024:
                        size_str = f"{size_bytes:.1f} {unit}"
                        break
                    size_bytes /= 1024
                else:
                    size_str = f"{size_bytes:.1f} TB"
                
                log_files.append({
                    'name': name,
                    'path': path,
                    'size': size_str,
                    'size_bytes': os.path.getsize(path)
                })
            else:
                log_files.append({
                    'name': name,
                    'path': path,
                    'size': '0 B',
                    'size_bytes': 0
                })
        except Exception:
            log_files.append({
                'name': name,
                'path': path,
                'size': 'unknown',
                'size_bytes': 0
            })
    
    # Sort by size (largest first)
    log_files.sort(key=lambda x: x['size_bytes'], reverse=True)
    return log_files

def get_js_verified_stats():
    """Get statistics about JavaScript-verified users."""
    js_log_file = JS_CAPABLE_LOG_FILE
    
    stats = {
        'verified_users': set(),  # Use sets to track unique UAs
        'verified_bots': set(),
        'consent_given': set(),   # Track unique UAs that gave consent
        'recent_verifications': [],
        'top_verified_ua': {},
        'top_verified_humans': {},
        'top_verified_bots': {},
        'top_failed_ua': {}
    }
    
    # Collect all entries for recent verifications
    all_entries = []
    
    # Process verified users log
    if os.path.exists(js_log_file):
        with open(js_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|')
                # New format: timestamp|BOT_DETECTION_RESULT|url|user_agent|bot_reason|consent_given
                # Old format: timestamp|BOT_DETECTION_RESULT|url|user_agent|bot_reason
                if len(parts) >= 6:
                    timestamp, bot_status, url, user_agent, reason, consent_given = parts[:6]
                elif len(parts) >= 5:
                    timestamp, bot_status, url, user_agent, reason = parts[:5]
                    consent_given = 'unknown'
                else:
                    continue
                
                # Track unique user agents
                ua_key = user_agent[:100]  # Truncate for grouping
                
                if bot_status == 'HUMAN_BY_UA':
                    stats['verified_users'].add(ua_key)  # Add to set for uniqueness
                    # Track human user agents separately
                    stats['top_verified_humans'][ua_key] = stats['top_verified_humans'].get(ua_key, 0) + 1
                elif bot_status == 'BOT':
                    stats['verified_bots'].add(ua_key)  # Add to set for uniqueness
                    # Track bot user agents separately
                    stats['top_verified_bots'][ua_key] = stats['top_verified_bots'].get(ua_key, 0) + 1
                
                # Track consent given (only for humans)
                if bot_status == 'HUMAN_BY_UA' and consent_given == 'true':
                    stats['consent_given'].add(ua_key)
                
                # Also track all verified UAs for backward compatibility
                stats['top_verified_ua'][ua_key] = stats['top_verified_ua'].get(ua_key, 0) + 1
                
                # Collect all entries first, then take the most recent 10
                all_entries.append({
                    'timestamp': timestamp,
                    'user_agent': user_agent[:50],
                    'status': bot_status,
                    'url': url[:50],
                    'consent_given': consent_given
                })
        
        # Sort by timestamp (most recent first) and take last 10
        all_entries.sort(key=lambda x: x['timestamp'], reverse=True)
        stats['recent_verifications'] = all_entries[:10]
    
    # Convert sets to counts for final stats
    unique_humans = len(stats['verified_users'])
    unique_bots = len(stats['verified_bots'])
    unique_consent = len(stats['consent_given'])
    
    # Replace sets with counts for template compatibility
    stats['verified_users'] = unique_humans
    stats['verified_bots'] = unique_bots
    stats['consent_given'] = unique_consent
    
    # Sort dictionaries by count (top 10)
    stats['top_verified_ua'] = dict(sorted(stats['top_verified_ua'].items(), key=lambda x: x[1], reverse=True)[:10])
    stats['top_verified_humans'] = dict(sorted(stats['top_verified_humans'].items(), key=lambda x: x[1], reverse=True)[:10])
    stats['top_verified_bots'] = dict(sorted(stats['top_verified_bots'].items(), key=lambda x: x[1], reverse=True)[:10])
    stats['top_failed_ua'] = dict(sorted(stats['top_failed_ua'].items(), key=lambda x: x[1], reverse=True)[:10])
    
    return stats

# Load bot patterns from well-known-bots.json for User-Agent detection
_bot_regex_patterns = []
_bot_simple_patterns = [
    'bot', 'crawler', 'spider', 'slurp', 'wget', 'curl', 'python-requests',
    'python-urllib', 'java/', 'libwww', 'httpclient', 'go-http-client',
    'scrapy', 'nutch', 'headlesschrome', 'phantomjs', 'prerender',
    'lighthouse', 'pagespeed', 'gtmetrix', 'playwright', 'claudebot', 'req/',
    'python-requests/', 'lotsoftools_url_checker'
]

def _ensure_log_dir():
    """Ensure the logs directory exists."""
    log_dir = os.path.dirname(UA_LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)


def _rotate_log_if_needed(log_file):
    """Rotate log file if it exceeds MAX_LOG_ENTRIES.
    
    Archives current log to .old and starts fresh.
    """
    try:
        if not os.path.exists(log_file):
            return
        
        # Count lines (quick check via file size estimate first)
        file_size = os.path.getsize(log_file)
        # If file is small (< 50MB), probably under 3M entries
        if file_size < 50_000_000:
            return
        
        # Count actual lines
        with open(log_file, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        
        if line_count >= MAX_LOG_ENTRIES:
            # Archive to .old (overwrite any existing .old)
            old_file = log_file + '.old'
            if os.path.exists(old_file):
                os.remove(old_file)
            os.rename(log_file, old_file)
            logger.info(f"Rotated log file {log_file} ({line_count} entries)")
    except Exception as e:
        logger.error(f"Failed to rotate log {log_file}: {e}")


def rotate_logs_on_startup():
    """Check and rotate all log files on app startup. Call once at init."""
    _ensure_log_dir()
    _rotate_log_if_needed(UA_LOG_FILE)
    _rotate_log_if_needed(REFERRER_LOG_FILE)
    _rotate_log_if_needed(ACCEPT_LANG_LOG_FILE)
    # Country log rotation is handled by country_block module


def _is_ua_definitive_bot(ua_lower):
    """Check if UA string itself indicates a definitive bot (old browser version, etc.).
    
    Used for old log entries that don't have a reason field.
    """
    # Chrome versions below 90
    chrome_match = re.search(r'chrome/(\d+)\.', ua_lower)
    if chrome_match and int(chrome_match.group(1)) < 90:
        return True
    # Firefox versions below 121
    firefox_match = re.search(r'firefox/(\d+)', ua_lower)
    if firefox_match and int(firefox_match.group(1)) < 121:
        return True
    # iOS versions below 14
    ios_match = re.search(r'cpu iphone os (\d+)_', ua_lower)
    if ios_match and int(ios_match.group(1)) < 14:
        return True
    # Android versions below 11
    android_match = re.search(r'android (\d+)', ua_lower)
    if android_match and int(android_match.group(1)) < 11:
        return True
    # Windows NT below 10
    windows_match = re.search(r'windows nt (\d+)\.', ua_lower)
    if windows_match and int(windows_match.group(1)) < 10:
        return True
    # Very old Windows
    if 'windows xp' in ua_lower or 'windows 2000' in ua_lower:
        return True
    return False


def _parse_ua_log():
    """Parse user agent log file and return aggregated stats.
    
    Log format: timestamp|BOT/HUMAN|url|user_agent
    Returns dict: {user_agent: {'count': N, 'is_bot': bool, 'js_verified': bool}}
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
                # Format: timestamp|BOT/HUMAN|url|user_agent|reason (5 parts)
                # Old format: timestamp|BOT/HUMAN|url|user_agent (4 parts)
                # Oldest format: timestamp|BOT/HUMAN|user_agent (3 parts)
                if len(parts) >= 5:
                    is_bot = parts[1].strip() == 'BOT'
                    ua = parts[3].strip()
                    reason = parts[4].strip()
                elif len(parts) >= 4:
                    is_bot = parts[1].strip() == 'BOT'
                    ua = parts[3].strip()
                    reason = ''
                else:
                    is_bot = parts[1].strip() == 'BOT'
                    ua = parts[2].strip()
                    reason = ''
                
                if ua not in stats:
                    stats[ua] = {'count': 0, 'is_bot': is_bot, 'js_verified': False, 'reason': reason}
                stats[ua]['count'] += 1
        
        # Now merge JS verification status
        if os.path.exists(JS_CAPABLE_LOG_FILE):
            with open(JS_CAPABLE_LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('|')
                    if len(parts) >= 5:
                        timestamp, bot_status, url, user_agent, bot_reason = parts[:5]
                        
                        # Mark as JS-verified if found in JS log
                        if user_agent in stats:
                            stats[user_agent]['js_verified'] = True
                            # Update bot status based on JS verification (more accurate)
                            stats[user_agent]['is_bot'] = (bot_status == 'BOT')
                            if bot_reason:
                                stats[user_agent]['reason'] = bot_reason
                        else:
                            # Add JS-only entries that weren't in UA log
                            stats[user_agent] = {
                                'count': 1,
                                'is_bot': (bot_status == 'BOT'),
                                'js_verified': True,
                                'reason': bot_reason
                            }
        
        return stats
    except Exception as e:
        logger.error(f"Error parsing UA log: {e}")
        return {}


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
    # LotsOfTools URL Checker
    if 'lotsoftools_url_checker' in ua_lower:
        return 'LotsOfTools'
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

def get_honeypot_agents():
    """Get honeypot agents from honeypot.log file."""
    honeypot_log_path = HONEYPOT_LOG_FILE
    agents = {}
    try:
        if os.path.exists(honeypot_log_path):
            with open(honeypot_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if line in agents:
                            agents[line] += 1
                        else:
                            agents[line] = 1
    except Exception as e:
        logger.error(f"Failed to parse honeypot log: {e}")
    
    # Convert to list of tuples sorted by count
    return sorted(agents.items(), key=lambda x: x[1], reverse=True)


def track_user_agent(user_agent, is_bot, url=None, bot_reason=None):
    """Log user agent to file for persistent tracking.
    
    Returns True if successfully logged as HUMAN, False otherwise.
    This return value MUST be used to gate human click counting - 
    ensuring log entries and click counts always match.
    """
    try:
        _ensure_log_dir()
        timestamp = datetime.now().isoformat()
        bot_label = 'BOT' if is_bot else 'HUMAN'
        # Sanitize user agent (remove newlines, limit length)
        ua_clean = user_agent.replace('\n', ' ').replace('|', ' ')[:500]
        url_clean = (url or '').replace('|', ' ')[:100]
        reason_clean = (bot_reason or '')[:100]
        log_entry = f"{timestamp}|{bot_label}|{url_clean}|{ua_clean}|{reason_clean}\n"
        
        with open(UA_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Only return True if we successfully wrote a HUMAN entry
        return not is_bot
    except Exception as e:
        logger.error(f"Failed to log user agent: {e}")
        return False  # Failed to log = count as bot


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


def _get_main_domain(domain):
    """Extract main domain from subdomains.
    
    Examples:
        'news.google.com' -> 'google.com'
        'mail.yahoo.co.uk' -> 'yahoo.co.uk'
        'subdomain.example.org' -> 'example.org'
    """
    try:
        # Split domain by dots
        parts = domain.split('.')
        
        # Handle common second-level TLDs like .co.uk, .de, .fr, etc.
        if len(parts) >= 3 and parts[-2] in {'co', 'com', 'org', 'net', 'gov', 'edu', 'mil'}:
            # For domains like example.co.uk -> example.co.uk
            return '.'.join(parts[-3:])
        elif len(parts) >= 2:
            # For regular domains like subdomain.example.com -> example.com
            return '.'.join(parts[-2:])
        else:
            # For single-part domains or malformed domains
            return domain
    except:
        return domain


def get_referrer_stats():
    """Get referrer statistics sorted by count descending."""
    stats = _parse_referrer_log()
    return sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)


def get_referrer_stats_by_domain():
    """Get referrer statistics aggregated by domain."""
    stats = _parse_referrer_log()
    domain_stats = {}
    
    # Domains to exclude
    excluded_domains = {'lotsoftools.net', 'lotsoftools.de', 'lotsoftools.pro', 'lotsof.tools'}
    
    for referrer, data in stats.items():
        if not data['is_bot']:  # Only count human referrers
            domain = _extract_referrer_domain(referrer)
            
            # Skip excluded domains
            if domain in excluded_domains:
                continue
            
            # Extract main domain (remove subdomains)
            main_domain = _get_main_domain(domain)
            
            # Skip if main domain is in excluded list
            if main_domain in excluded_domains:
                continue
            
            if main_domain in domain_stats:
                domain_stats[main_domain] += data['count']
            else:
                domain_stats[main_domain] = data['count']
    
    return domain_stats


def track_accept_language(accept_lang, url=None):
    """Log Accept-Language header for humans only."""
    if not accept_lang:
        return
    try:
        _ensure_log_dir()
        timestamp = datetime.now().isoformat()
        # Sanitize (remove newlines, limit length)
        lang_clean = accept_lang.replace('\n', ' ').replace('|', ' ')[:200]
        url_clean = (url or '').replace('|', ' ')[:100]
        log_entry = f"{timestamp}|{url_clean}|{lang_clean}\n"
        
        with open(ACCEPT_LANG_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to log accept-language: {e}")


def _extract_primary_language(accept_lang):
    """Extract primary language code from Accept-Language header.
    
    e.g. 'de-DE,de;q=0.9,en;q=0.8' -> 'de'
         'en-US,en;q=0.9' -> 'en'
    """
    if not accept_lang:
        return None
    # Take first language (highest priority), strip region
    first = accept_lang.split(',')[0].strip()
    lang = first.split(';')[0].strip()  # Remove quality value
    lang = lang.split('-')[0].strip()   # Remove region (de-DE -> de)
    return lang.lower() if lang else None


def _parse_accept_language_log():
    """Parse Accept-Language log and return primary language counts."""
    stats = {}
    try:
        if not os.path.exists(ACCEPT_LANG_LOG_FILE):
            return stats
        with open(ACCEPT_LANG_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                parts = line.split('|')
                if len(parts) >= 3:
                    accept_lang = parts[2].strip()
                    primary = _extract_primary_language(accept_lang)
                    if primary:
                        stats[primary] = stats.get(primary, 0) + 1
    except Exception as e:
        logger.error(f"Failed to parse accept-language log: {e}")
    return stats


def get_accept_language_stats():
    """Get Accept-Language statistics sorted by count descending."""
    stats = _parse_accept_language_log()
    # Sort by count descending
    return sorted(stats.items(), key=lambda x: x[1], reverse=True)


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
    from app.services.bot_detection import is_bot_request as bot_detection_is_bot_request
    return bot_detection_is_bot_request()

def enhanced_bot_detection():
    """Enhanced bot detection that considers JavaScript capability."""
    from app.services.bot_detection import enhanced_bot_detection as enhanced_detection
    return enhanced_detection()

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
        is_bot, bot_reason = enhanced_bot_detection()
        
        # track_user_agent returns True ONLY if successfully logged as HUMAN
        # This is the source of truth for click counting - ensures log and count match
        logged_as_human = track_user_agent(user_agent, is_bot, url, bot_reason)
        
        track_referrer(referrer, is_bot, url)
        # Track country
        from app.services.country_block import get_client_ip, get_country_code, track_country
        ip = get_client_ip()
        country = get_country_code(ip)
        track_country(country, is_bot, url)
        
        # Use logged_as_human as the gate - if not logged as human, count as bot
        if not logged_as_human:
            link.bot_click_count = (link.bot_click_count or 0) + 1
            link.bot_bytes_served = (link.bot_bytes_served or 0) + 0
        else:
            link.click_count = (link.click_count or 0) + 1
            link.bytes_served = (link.bytes_served or 0) + 0
            
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
            
            # Track device type from Sec-CH-UA-Mobile header (only for humans)
            is_mobile = request.headers.get('Sec-CH-UA-Mobile', '') == '?1'
            if is_mobile:
                link.mobile_clicks = (link.mobile_clicks or 0) + 1
            else:
                link.desktop_clicks = (link.desktop_clicks or 0) + 1
            
            # Track Accept-Language header (only for humans)
            accept_lang = request.headers.get('Accept-Language', '')
            track_accept_language(accept_lang, url)
        
        db.session.commit()
        return True
    return False

def increment_bot_click_count(url, user_agent, reason):
    """Increment bot click count directly (for honeypot links)."""
    link = get_link_by_url(url)
    if link:
        # Track as bot in logs
        track_user_agent(user_agent, True, url, reason)
        
        # Increment bot click count
        link.bot_click_count = (link.bot_click_count or 0) + 1
        link.bot_bytes_served = (link.bot_bytes_served or 0) + 0
        
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
        'mobile_clicks': link.mobile_clicks or 0,
        'desktop_clicks': link.desktop_clicks or 0,
        'bytes_served': link.bytes_served or 0,
        'bot_bytes_served': link.bot_bytes_served or 0,
        'is_meta_link': link.is_meta_link or False
    } for link in links]

def get_theme_language_totals():
    """Get total counts for theme, language, and device across all links."""
    links = Link.query.all()
    light = sum(link.light_clicks or 0 for link in links)
    dark = sum(link.dark_clicks or 0 for link in links)
    high_contrast = sum(link.high_contrast_clicks or 0 for link in links)
    system_theme = sum(link.system_theme_clicks or 0 for link in links)
    total_theme = light + dark + high_contrast + system_theme
    mobile = sum(link.mobile_clicks or 0 for link in links)
    desktop = sum(link.desktop_clicks or 0 for link in links)
    total_device = mobile + desktop
    totals = {
        'light': light,
        'dark': dark,
        'high_contrast': high_contrast,
        'system_theme': system_theme,
        'system_theme_pct': round(system_theme / total_theme * 100, 1) if total_theme > 0 else 0,
        'en': sum(link.en_clicks or 0 for link in links),
        'de': sum(link.de_clicks or 0 for link in links),
        'mobile': mobile,
        'desktop': desktop,
        'mobile_pct': round(mobile / total_device * 100, 1) if total_device > 0 else 0,
        'desktop_pct': round(desktop / total_device * 100, 1) if total_device > 0 else 0
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
