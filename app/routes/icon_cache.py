from flask import Blueprint, jsonify
import requests
import json
import os
from datetime import datetime, timedelta

icon_cache_bp = Blueprint('icon_cache', __name__, url_prefix='/api')

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache')
FA_CACHE_FILE = os.path.join(CACHE_DIR, 'fontawesome_icons.json')
LUCIDE_CACHE_FILE = os.path.join(CACHE_DIR, 'lucide_icons.json')
CACHE_DURATION = timedelta(days=2)

# In-memory cache with size limit
_memory_cache = {
    'fontawesome': None,
    'lucide': None,
    'fontawesome_time': None,
    'lucide_time': None
}
_MAX_CACHE_SIZE_MB = 50  # Maximum memory cache size in MB

def ensure_cache_dir():
    """Ensure cache directory exists"""
    os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_size_mb():
    """Get approximate size of memory cache in MB."""
    import sys
    total_size = 0
    for key, value in _memory_cache.items():
        if value is not None and not key.endswith('_time'):
            total_size += sys.getsizeof(value)
    return total_size / (1024 * 1024)

def _clear_cache_if_needed():
    """Clear memory cache if it exceeds size limit."""
    cache_size_mb = _get_cache_size_mb()
    if cache_size_mb > _MAX_CACHE_SIZE_MB:
        print(f"Memory cache size ({cache_size_mb:.2f}MB) exceeds limit, clearing cache")
        _memory_cache['fontawesome'] = None
        _memory_cache['lucide'] = None
        _memory_cache['fontawesome_time'] = None
        _memory_cache['lucide_time'] = None

def is_cache_valid(cache_time):
    """Check if cache is still valid (less than 2 days old)"""
    if cache_time is None:
        return False
    return datetime.now() - cache_time < CACHE_DURATION

def load_from_disk(cache_file):
    """Load cache from disk"""
    if not os.path.exists(cache_file):
        return None, None
    
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
            cache_time = datetime.fromisoformat(data['timestamp'])
            return data['icons'], cache_time
    except Exception as e:
        print(f"Error loading cache from {cache_file}: {e}")
        return None, None

def save_to_disk(cache_file, icons):
    """Save cache to disk"""
    ensure_cache_dir()
    try:
        data = {
            'timestamp': datetime.now().isoformat(),
            'icons': icons
        }
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving cache to {cache_file}: {e}")

def fetch_fontawesome_icons():
    """Fetch Font Awesome icons from GitHub"""
    try:
        response = requests.get('https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/metadata/icons.json', timeout=30)
        response.raise_for_status()
        data = response.json()
        
        icons = []
        for icon_name, icon_data in data.items():
            if icon_data.get('free') and 'solid' in icon_data.get('free', []):
                category = icon_data.get('search', {}).get('terms', ['other'])[0] if icon_data.get('search', {}).get('terms') else 'other'
                icons.append({
                    'name': icon_name,
                    'class': f'fas fa-{icon_name}',
                    'category': category.lower(),
                    'library': 'fontawesome',
                    'tags': icon_data.get('search', {}).get('terms', [])
                })
        
        return icons
    except Exception as e:
        print(f"Error fetching Font Awesome icons: {e}")
        return None

def fetch_lucide_icons():
    """Fetch Lucide icons from CDN"""
    try:
        response = requests.get('https://unpkg.com/lucide-static@latest/tags.json', timeout=30)
        response.raise_for_status()
        data = response.json()
        
        icons = []
        for name, tags in data.items():
            icons.append({
                'name': name,
                'category': tags[0] if tags else 'other',
                'tags': tags,
                'library': 'lucide'
            })
        
        return icons
    except Exception as e:
        print(f"Error fetching Lucide icons: {e}")
        return None

def get_icons(library):
    """Get icons for a library, using cache if available"""
    cache_file = FA_CACHE_FILE if library == 'fontawesome' else LUCIDE_CACHE_FILE
    fetch_func = fetch_fontawesome_icons if library == 'fontawesome' else fetch_lucide_icons
    
    # Clear cache if it exceeds size limit
    _clear_cache_if_needed()
    
    # Check memory cache first
    if _memory_cache[library] and is_cache_valid(_memory_cache[f'{library}_time']):
        print(f"Using memory cache for {library}")
        return _memory_cache[library]
    
    # Check disk cache
    icons, cache_time = load_from_disk(cache_file)
    if icons and is_cache_valid(cache_time):
        print(f"Using disk cache for {library}")
        _memory_cache[library] = icons
        _memory_cache[f'{library}_time'] = cache_time
        return icons
    
    # Fetch from CDN
    print(f"Fetching {library} icons from CDN")
    icons = fetch_func()
    
    if icons:
        # Save to both memory and disk cache
        _memory_cache[library] = icons
        _memory_cache[f'{library}_time'] = datetime.now()
        save_to_disk(cache_file, icons)
        return icons
    
    # If fetch failed, return stale cache if available
    if icons is None and _memory_cache[library]:
        print(f"Using stale cache for {library}")
        return _memory_cache[library]
    
    return []

@icon_cache_bp.route('/icons/fontawesome')
def fontawesome_icons():
    """Get Font Awesome icons"""
    icons = get_icons('fontawesome')
    return jsonify(icons)

@icon_cache_bp.route('/icons/lucide')
def lucide_icons():
    """Get Lucide icons"""
    icons = get_icons('lucide')
    return jsonify(icons)

@icon_cache_bp.route('/icons/all')
def all_icons():
    """Get all icons from both libraries"""
    fa_icons = get_icons('fontawesome')
    lucide_icons = get_icons('lucide')
    return jsonify({
        'fontawesome': fa_icons,
        'lucide': lucide_icons
    })
