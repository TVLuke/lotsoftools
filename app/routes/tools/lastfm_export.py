import io
import json
import os
import requests
from flask import Blueprint, render_template, request, jsonify, Response
from app.services.link_service import increment_click_count

lastfm_export_bp = Blueprint('lastfm_export', __name__, url_prefix='/tools')

LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"


def get_lastfm_config():
    """Load last.fm config from ENV or config file"""
    # Try environment variables first
    api_key = os.environ.get('LASTFM_API_KEY', '').strip()
    username = os.environ.get('LASTFM_USERNAME', '').strip()
    secret = os.environ.get('LASTFM_SECRET', '').strip()
    
    # Fall back to config file
    if not api_key or not username:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'lastfm_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if not api_key:
                        api_key = config.get('api_key', '').strip()
                    if not username:
                        username = config.get('username', '').strip()
                    if not secret:
                        secret = config.get('secret', '').strip()
            except Exception:
                pass
    
    return {
        'api_key': api_key,
        'username': username,
        'secret': secret
    }


def fetch_recent_tracks(api_key, username, page=1, limit=200):
    """Fetch recent tracks from last.fm API"""
    params = {
        'method': 'user.getrecenttracks',
        'user': username,
        'api_key': api_key,
        'limit': limit,
        'page': page,
        'format': 'json'
    }
    
    response = requests.get(LASTFM_API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def extract_tracks(data):
    """Extract track info from API response - matches original format"""
    tracks = []
    
    recent_tracks = data.get('recenttracks', {}).get('track', [])
    
    for track in recent_tracks:
        # Skip currently playing track (has no date)
        if track.get('@attr', {}).get('nowplaying') == 'true':
            continue
        
        # Format: artist, album, name, date (4 columns)
        tracks.append({
            'artist': track.get('artist', {}).get('#text', ''),
            'album': track.get('album', {}).get('#text', ''),
            'name': track.get('name', ''),
            'date': track.get('date', {}).get('#text', ''),
        })
    
    return tracks


def get_total_pages(data):
    """Get total page count from API response"""
    attr = data.get('recenttracks', {}).get('@attr', {})
    return int(attr.get('totalPages', 1))


def get_total_tracks(data):
    """Get total track count from API response"""
    attr = data.get('recenttracks', {}).get('@attr', {})
    return int(attr.get('total', 0))


@lastfm_export_bp.route('/lastfm-export')
def index():
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'lastfm_export_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    # Check if API key is configured (don't expose the key itself!)
    config = get_lastfm_config()
    api_configured = bool(config['api_key'])
    
    return render_template('tools/lastfm_export.html', 
                          tool_data=tool_data,
                          api_configured=api_configured)


@lastfm_export_bp.route('/lastfm-export/info', methods=['POST'])
def get_info():
    """Get user info and total track count"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Use server-side API key
    config = get_lastfm_config()
    api_key = config['api_key']
    
    if not api_key:
        return jsonify({'error': 'API key not configured on server'}), 500
    
    try:
        # Use limit=200 to get correct page count (same as actual fetch)
        result = fetch_recent_tracks(api_key, username, page=1, limit=200)
        
        if 'error' in result:
            return jsonify({'error': result.get('message', 'API error')}), 400
        
        total_tracks = get_total_tracks(result)
        total_pages = get_total_pages(result)
        
        return jsonify({
            'success': True,
            'total_tracks': total_tracks,
            'total_pages': total_pages
        })
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to connect to last.fm: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@lastfm_export_bp.route('/lastfm-export/fetch', methods=['POST'])
def fetch_page():
    """Fetch a single page of tracks"""
    data = request.get_json()
    username = data.get('username', '').strip()
    page = data.get('page', 1)
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    # Use server-side API key
    config = get_lastfm_config()
    api_key = config['api_key']
    
    if not api_key:
        return jsonify({'error': 'API key not configured on server'}), 500
    
    try:
        result = fetch_recent_tracks(api_key, username, page=page, limit=200)
        
        if 'error' in result:
            return jsonify({'error': result.get('message', 'API error')}), 400
        
        tracks = extract_tracks(result)
        
        return jsonify({
            'success': True,
            'tracks': tracks,
            'page': page
        })
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to connect to last.fm: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def csv_escape(value):
    """Match original JS: remove commas and quotes from strings"""
    if isinstance(value, str):
        return value.replace('"', '').replace(',', '')
    return value if value is not None else ''


@lastfm_export_bp.route('/lastfm-export/download', methods=['POST'])
def download_csv():
    """Generate CSV from provided tracks data - matches original JS implementation"""
    data = request.get_json()
    tracks = data.get('tracks', [])
    username = data.get('username', 'lastfm')
    
    if not tracks:
        return jsonify({'error': 'No tracks provided'}), 400
    
    # Format: artist, album, name, date (4 columns, no header)
    lines = []
    for track in tracks:
        row = [
            csv_escape(track.get('artist', '')),
            csv_escape(track.get('album', '')),
            csv_escape(track.get('name', '')),
            csv_escape(track.get('date', ''))
        ]
        lines.append(','.join(row))
    
    csv_content = '\n'.join(lines) + '\n'
    
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={username}_lastfm_history.csv'
        }
    )
