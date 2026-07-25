from flask import Blueprint, render_template, request, make_response, jsonify, session, Response, send_from_directory
import os
import hashlib
from functools import wraps
from app import db
import csv
import io
import uuid
from datetime import datetime
from app.services import link_service
from app.services.blocklist_service import get_blocklist_info, get_blocked_request_count

# Random ID generated once per instance startup
INSTANCE_ID = uuid.uuid4().hex[:8]

def get_stats_password():
    """Get stats password from environment (read at request time)."""
    return os.environ.get('STATS_PASSWORD', '')

def check_stats_auth():
    """Check if user is authenticated for stats page."""
    stats_password = get_stats_password().strip()  # Strip whitespace
    
    # Check cookie first
    auth_cookie = request.cookies.get('stats_auth', '')
    if auth_cookie and stats_password:
        expected = hashlib.sha256(stats_password.encode()).hexdigest()[:16]
        if auth_cookie == expected:
            return True
    
    # Check HTTP Basic Auth
    auth = request.authorization
    if auth and stats_password:
        if auth.username == 'user' and auth.password == stats_password:
            return True
    
    return False

def require_stats_auth(f):
    """Decorator to require authentication for stats routes (HTML page)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_stats_auth():
            resp = Response('Authentication required', status=401)
            resp.headers['WWW-Authenticate'] = 'Basic realm="Stats"'
            return resp
        
        # Execute the route
        response = f(*args, **kwargs)
        
        # Set auth cookie if authenticated via Basic Auth (not already via cookie)
        auth_cookie = request.cookies.get('stats_auth', '')
        if not auth_cookie and request.authorization:
            if hasattr(response, 'set_cookie'):
                stats_password = get_stats_password().strip()
                expected = hashlib.sha256(stats_password.encode()).hexdigest()[:16]
                response.set_cookie('stats_auth', expected, max_age=86400*30, httponly=True, samesite='Lax')
        
        return response
    return decorated

def require_stats_api_auth(f):
    """Decorator to require header-based auth for stats API/CSV routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        stats_password = get_stats_password()
        
        # Check X-Stats-Password header
        header_password = request.headers.get('X-Stats-Password', '')
        if header_password == stats_password:
            return f(*args, **kwargs)
        
        return Response('Unauthorized', 401)
    return decorated

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    link_service.increment_click_count('/')
    desktop_layout = request.cookies.get('desktop_layout', 'categorized')
    mobile_layout = request.cookies.get('mobile_layout', 'compact')
    
    lang = session.get('lang', 'en')
    categories = link_service.get_links_by_category(lang)
    
    all_links = []
    seen_urls = set()
    
    for category_links in categories.values():
        for link in category_links:
            if link['url'] not in seen_urls:
                all_links.append(link)
                seen_urls.add(link['url'])
    
    all_links.sort(key=lambda x: x.get('name', '').lower())
    
    return render_template('index.html',
                         categories=categories,
                         all_links=all_links,
                         desktop_layout=desktop_layout,
                         mobile_layout=mobile_layout)

@main_bp.route('/api/layout/desktop', methods=['POST'])
def set_desktop_layout():
    data = request.get_json()
    if not data or 'layout' not in data:
        return jsonify({'success': False, 'message': 'Layout is required'}), 400
    
    layout = data['layout']
    if layout not in ['categorized', 'compact']:
        return jsonify({'success': False, 'message': 'Invalid layout'}), 400
    
    response = make_response(jsonify({'success': True, 'message': 'Desktop layout updated'}))
    response.set_cookie('desktop_layout', layout, max_age=31536000)
    return response

@main_bp.route('/api/layout/mobile', methods=['POST'])
def set_mobile_layout():
    data = request.get_json()
    if not data or 'layout' not in data:
        return jsonify({'success': False, 'message': 'Layout is required'}), 400
    
    layout = data['layout']
    if layout not in ['categorized', 'compact']:
        return jsonify({'success': False, 'message': 'Invalid layout'}), 400
    
    response = make_response(jsonify({'success': True, 'message': 'Mobile layout updated'}))
    response.set_cookie('mobile_layout', layout, max_age=31536000)
    return response


@main_bp.route('/api/language/<lang>', methods=['POST'])
def set_language(lang):
    if lang in ['en', 'de']:
        session['lang'] = lang
        response = make_response(jsonify({'success': True, 'language': lang}))
        response.set_cookie('lotsoftools_lang', lang, max_age=31536000, samesite='Lax')
        return response
    return jsonify({'success': False, 'message': 'Invalid language'}), 400


@main_bp.route('/sitemap')
def sitemap():
    """Site-wide sitemap with all tools and their sub-pages."""
    from app.services import link_service
    
    # Get all tools from link service
    lang = session.get('lang', 'en')
    categories = link_service.get_links_by_category(lang)
    
    # Collect sitemap entries from tools that provide them
    tool_sitemaps = []
    
    # Import and call get_sitemap_entries from tools that have it
    try:
        from app.routes.tools.holiday_calendar import get_sitemap_entries as holiday_sitemap
        tool_sitemaps.append(holiday_sitemap())
    except (ImportError, AttributeError):
        pass
    
    return render_template('sitemap.html',
                          categories=categories,
                          tool_sitemaps=tool_sitemaps)

@main_bp.route('/stats')
@require_stats_auth
def stats():
    # Don't track /stats clicks - distorts the numbers
    links = link_service.get_links_stats()
    
    # Logging is disabled, so these stats are no longer available
    user_agents = []
    bot_user_agents = []
    human_user_agents = []
    honeypot_agents = []
    referrer_stats = []
    country_stats = []
    accept_language_stats = []
    js_verified_stats = {'verified_users': 0, 'verified_bots': 0, 'consent_given': 0, 'recent_verifications': [], 
                        'top_verified_ua': {}, 'top_verified_humans': {}, 'top_verified_bots': {}, 'top_failed_ua': {}}
    
    server_start_time = link_service.get_server_start_time()
    theme_lang_totals = link_service.get_theme_language_totals()
    ua_log_size = "0 B (logging disabled)"
    all_log_sizes = []
    blocklist_info = get_blocklist_info()
    blocked_count = 0
    
    response = make_response(render_template('stats.html', links=links, user_agents=user_agents, 
                          bot_user_agents=bot_user_agents, human_user_agents=human_user_agents,
                          honeypot_agents=honeypot_agents, referrer_stats=referrer_stats, country_stats=country_stats,
                          accept_language_stats=accept_language_stats,
                          server_start_time=server_start_time, instance_id=INSTANCE_ID,
                          theme_lang_totals=theme_lang_totals, ua_log_size=ua_log_size, all_log_sizes=all_log_sizes, js_verified_stats=js_verified_stats,
                          blocklist_info=blocklist_info, blocked_count=blocked_count))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main_bp.route('/stats.csv')
@require_stats_api_auth
def stats_csv():
    links = link_service.get_links_stats()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'url', 'click_count', 'bot_click_count', 'light_clicks', 'dark_clicks', 'high_contrast_clicks', 'system_theme_clicks', 'en_clicks', 'de_clicks', 'mobile_clicks', 'desktop_clicks'])
    
    for link in links:
        writer.writerow([link['name'], link['url'], link['click_count'], link['bot_click_count'], 
                        link['light_clicks'], link['dark_clicks'], link['high_contrast_clicks'], link['system_theme_clicks'],
                        link['en_clicks'], link['de_clicks'], link['mobile_clicks'], link['desktop_clicks']])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=stats.csv'
    return response

@main_bp.route('/stats/blocklist.csv')
@require_stats_api_auth
def stats_blocklist_csv():
    blocklist_info = get_blocklist_info()
    blocked_count = get_blocked_request_count()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['timestamp', 'enabled', 'domains_loaded', 'lists_loaded', 'blocked_requests'])
    writer.writerow([
        datetime.now().isoformat(),
        blocklist_info.get('enabled', False),
        blocklist_info.get('domain_count', 0),
        blocklist_info.get('lists_loaded', 0),
        blocked_count
    ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=blocklist.csv'
    return response

@main_bp.route('/stats/user_agents.csv')
@require_stats_api_auth
def stats_user_agents_csv():
    # Logging is disabled, return empty data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['company', 'count'])
    writer.writerow(['Logging disabled', 0])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=user_agents.csv'
    return response

@main_bp.route('/stats/countries.csv')
@require_stats_api_auth
def stats_countries_csv():
    # Logging is disabled, return empty data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['country', 'human_count', 'bot_count'])
    writer.writerow(['Logging disabled', 0, 0])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=countries.csv'
    return response

@main_bp.route('/stats/referrers.csv')
@require_stats_api_auth
def stats_referrers_csv():
    # Logging is disabled, return empty data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['domain', 'count'])
    writer.writerow(['Logging disabled', 0])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=referrers.csv'
    return response

@main_bp.route('/stats/browser_languages.csv')
@require_stats_api_auth
def stats_browser_languages_csv():
    # Logging is disabled, return empty data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['language', 'count'])
    writer.writerow(['Logging disabled', 0])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=browser_languages.csv'
    return response

@main_bp.route('/about')
def about():
    link_service.increment_click_count('/about')
    from app.services.about_content import load_about_content
    lang = session.get('lang', 'en')
    about_content = load_about_content(lang)
    return render_template('about.html', about_content=about_content)

@main_bp.route('/privacy')
@main_bp.route('/datenschutz')
def privacy():
    """Privacy policy page with tool-specific privacy information."""
    link_service.increment_click_count('/privacy')
    from app.models import Link
    from app.services.privacy_content import load_privacy_content
    
    lang = session.get('lang', 'en')
    
    # Load custom privacy content
    privacy_content = load_privacy_content(lang)
    
    # Get all active links with privacy info
    links = Link.query.order_by(Link._name).all()
    
    tools_privacy = []
    for link in links:
        tools_privacy.append({
            'name': link.get_name(lang),
            'url': link.url,
            'frontend_only': link.frontend_only,
            'uses_external_service': link.uses_external_service
        })
    
    # Sort by name
    tools_privacy.sort(key=lambda x: x['name'].lower())
    
    return render_template('privacy.html', tools=tools_privacy, privacy_content=privacy_content)

@main_bp.route('/accessibility')
@main_bp.route('/accessibility/<path:filename>')
def accessibility_report(filename='index.html'):
    """Serve the accessibility test report."""
    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'accessibility-report')
    return send_from_directory(report_dir, filename)

@main_bp.route('/accessibility-statement')
@main_bp.route('/barrierefreiheit')
def accessibility_statement():
    """Accessibility statement page."""
    link_service.increment_click_count('/accessibility-statement')
    return render_template('accessibility_statement.html')

@main_bp.route('/bot-policy')
@main_bp.route('/bot-policy')
def bot_policy():
    """Bot policy page - honeypot for bots."""
    # Use normal increment_click_count - bot_detection will handle the honeypot logic
    link_service.increment_click_count('/bot-policy')
    return render_template('bot_policy.html')

@main_bp.route('/third-party-libraries')
@main_bp.route('/drittanbieter-bibliotheken')
def third_party_libraries():
    """Third-party libraries page with license information."""
    import json
    libraries_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'libraries.json')
    
    libraries = []
    generated_at = None
    
    if os.path.exists(libraries_file):
        with open(libraries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            libraries = data.get('libraries', [])
            generated_at = data.get('generated_at')
    
    return render_template('third_party_libraries.html', libraries=libraries, generated_at=generated_at)

@main_bp.route('/.well-known/security.txt')
@main_bp.route('/security.txt')
def security_txt():
    """Serve security.txt file with correct content type and dynamic expiration."""
    try:
        from datetime import datetime, timedelta
        
        # Calculate expiration date (1 year from now)
        expires_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        # Render template with dynamic date
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'security.txt')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Simple template rendering (replace {{ expires_date }})
        content = template_content.replace('{{ expires_date }}', expires_date)
        
        response = make_response(content)
        response.headers['Content-Type'] = 'text/plain'
        return response
        
    except Exception as e:
        return "Error serving security file", 500
