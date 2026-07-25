"""Country-based IP blocking service using GeoIP2."""
import os
import json
import logging
from datetime import datetime
from flask import request, abort

logger = logging.getLogger(__name__)

# Path to blocked countries config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'blocked_countries.json')

# GeoIP database path
GEOIP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'geoip_data')
CITY_DB_PATH = os.path.join(GEOIP_DIR, 'GeoLite2-City.mmdb')

# Log file for country tracking
COUNTRY_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'logs', 'countries.log')

# Log rotation settings
MAX_LOG_ENTRIES = 3_000_000
MAX_LOG_SIZE_MB = 100  # Also rotate if file exceeds 100MB

# Disable logging
LOGGING_ENABLED = False

# Cache for config
_blocked_countries = None
_geoip_reader = None


def _load_config():
    """Load blocked countries configuration."""
    global _blocked_countries
    if _blocked_countries is not None:
        return _blocked_countries
    
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                _blocked_countries = {
                    'enabled': config.get('enabled', False),
                    'countries': set(c.upper() for c in config.get('blocked_country_codes', []))
                }
        else:
            _blocked_countries = {'enabled': False, 'countries': set()}
    except Exception as e:
        logger.error(f"Failed to load country block config: {e}")
        _blocked_countries = {'enabled': False, 'countries': set()}
    
    return _blocked_countries


def _get_geoip_reader():
    """Get or create GeoIP reader."""
    global _geoip_reader
    if _geoip_reader is not None:
        return _geoip_reader
    
    try:
        import geoip2.database
        if os.path.exists(CITY_DB_PATH):
            _geoip_reader = geoip2.database.Reader(CITY_DB_PATH)
        else:
            logger.warning(f"GeoIP database not found at {CITY_DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize GeoIP reader: {e}")
    
    return _geoip_reader


def get_client_ip():
    """Get the client's real IP address, considering proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


def get_country_code(ip):
    """Get country code for an IP address."""
    reader = _get_geoip_reader()
    if not reader:
        return None
    
    try:
        import geoip2.errors
        response = reader.city(ip)
        return response.country.iso_code
    except geoip2.errors.AddressNotFoundError:
        return None
    except Exception as e:
        logger.error(f"GeoIP lookup failed for {ip}: {e}")
        return None


def is_country_blocked(ip=None):
    """Check if an IP's country is blocked."""
    config = _load_config()
    if not config['enabled'] or not config['countries']:
        return False
    
    if ip is None:
        ip = get_client_ip()
    
    country_code = get_country_code(ip)
    if country_code and country_code.upper() in config['countries']:
        return True
    
    return False


def check_country_block():
    """Check if request should be blocked based on country. Call from before_request."""
    config = _load_config()
    if not config['enabled'] or not config['countries']:
        return
    
    ip = get_client_ip()
    country_code = get_country_code(ip)
    
    if country_code and country_code.upper() in config['countries']:
        # Track the blocked request before aborting
        track_country(country_code, is_bot=True, url=request.path)  # Count as bot for stats
        abort(403)


def get_blocked_countries_info():
    """Get info about blocked countries for stats page."""
    config = _load_config()
    return {
        'enabled': config['enabled'],
        'countries': list(config['countries']),
        'count': len(config['countries'])
    }


def reload_config():
    """Force reload of configuration."""
    global _blocked_countries
    _blocked_countries = None
    _load_config()


def _ensure_log_dir():
    """Ensure the log directory exists."""
    log_dir = os.path.dirname(COUNTRY_LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)


def _rotate_log_if_needed():
    """Rotate country log file if it exceeds MAX_LOG_ENTRIES or MAX_LOG_SIZE_MB."""
    try:
        if not os.path.exists(COUNTRY_LOG_FILE):
            return
        
        file_size = os.path.getsize(COUNTRY_LOG_FILE)
        file_size_mb = file_size / (1024 * 1024)
        
        # Rotate if file is too large (> 100MB)
        if file_size_mb > MAX_LOG_SIZE_MB:
            old_file = COUNTRY_LOG_FILE + '.old'
            if os.path.exists(old_file):
                os.remove(old_file)
            os.rename(COUNTRY_LOG_FILE, old_file)
            logger.info(f"Rotated country log (size: {file_size_mb:.2f}MB)")
            return
        
        # If file is small (< 50MB), probably under 3M entries
        if file_size < 50_000_000:
            return
        
        # Count actual lines
        with open(COUNTRY_LOG_FILE, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        
        if line_count >= MAX_LOG_ENTRIES:
            # Archive to .old (overwrite any existing .old)
            old_file = COUNTRY_LOG_FILE + '.old'
            if os.path.exists(old_file):
                os.remove(old_file)
            os.rename(COUNTRY_LOG_FILE, old_file)
            logger.info(f"Rotated country log ({line_count} entries)")
    except Exception as e:
        logger.error(f"Failed to rotate country log: {e}")


def rotate_country_log_on_startup():
    """Check and rotate country log on app startup."""
    _ensure_log_dir()
    _rotate_log_if_needed()
    _cleanup_old_log_files()

def _cleanup_old_log_files():
    """Remove .old log files that are too large (> 200MB) to prevent disk bloat."""
    try:
        old_file = COUNTRY_LOG_FILE + '.old'
        if os.path.exists(old_file):
            file_size_mb = os.path.getsize(old_file) / (1024 * 1024)
            if file_size_mb > 200:  # Remove .old files larger than 200MB
                os.remove(old_file)
                logger.info(f"Removed large old country log file: {old_file} ({file_size_mb:.2f}MB)")
    except Exception as e:
        logger.error(f"Failed to cleanup old country log file: {e}")


def track_country(country_code, is_bot, url=None):
    """Log country to file for persistent tracking.
    
    LOGGING DISABLED - Function does nothing
    """
    if not LOGGING_ENABLED or not country_code:
        return
    try:
        _ensure_log_dir()
        timestamp = datetime.now().isoformat()
        bot_label = 'BOT' if is_bot else 'HUMAN'
        url_clean = (url or '').replace('|', ' ')[:100]
        log_entry = f"{timestamp}|{bot_label}|{url_clean}|{country_code}\n"
        
        with open(COUNTRY_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to log country: {e}")


def _parse_country_log():
    """Parse country log file and return aggregated stats.
    
    Log format: timestamp|BOT/HUMAN|url|country_code
    Returns dict: {country_code: {'human': N, 'bot': N}}
    """
    stats = {}
    try:
        if not os.path.exists(COUNTRY_LOG_FILE):
            return stats
        
        file_size_mb = os.path.getsize(COUNTRY_LOG_FILE) / (1024 * 1024)
        
        # If file is too large (> 50MB), only process recent entries
        if file_size_mb > 50:
            logger.warning(f"Country log file is large ({file_size_mb:.2f}MB), processing only recent entries")
            with open(COUNTRY_LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-10000:]  # Only last 10k lines
        else:
            with open(COUNTRY_LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or '|' not in line:
                continue
            parts = line.split('|')
            if len(parts) >= 4:
                is_bot = parts[1].strip() == 'BOT'
                country = parts[3].strip().upper()
                if country not in stats:
                    stats[country] = {'human': 0, 'bot': 0}
                if is_bot:
                    stats[country]['bot'] += 1
                else:
                    stats[country]['human'] += 1
    except Exception as e:
        logger.error(f"Failed to parse country log: {e}")
    return stats


def get_country_stats():
    """Get country statistics sorted by human count descending."""
    stats = _parse_country_log()
    return sorted(stats.items(), key=lambda x: x[1]['human'], reverse=True)
