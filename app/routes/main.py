from flask import Blueprint, render_template, request, make_response, jsonify, session, Response, send_from_directory
import os
from app import db
import csv
import io
import uuid
from datetime import datetime
from app.services import link_service
from app.services.blocklist_service import get_blocklist_info, get_blocked_request_count

# Random ID generated once per instance startup
INSTANCE_ID = uuid.uuid4().hex[:8]

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
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
def stats():
    links = link_service.get_links_stats()
    user_agents = link_service.get_user_agent_stats()
    bot_user_agents = link_service.get_bot_user_agents()
    human_user_agents = link_service.get_human_user_agents()
    server_start_time = link_service.get_server_start_time()
    theme_lang_totals = link_service.get_theme_language_totals()
    ua_log_size = link_service.get_ua_log_file_size()
    blocklist_info = get_blocklist_info()
    blocked_count = get_blocked_request_count()
    response = make_response(render_template('stats.html', links=links, user_agents=user_agents, 
                          bot_user_agents=bot_user_agents, human_user_agents=human_user_agents,
                          server_start_time=server_start_time, instance_id=INSTANCE_ID,
                          theme_lang_totals=theme_lang_totals, ua_log_size=ua_log_size,
                          blocklist_info=blocklist_info, blocked_count=blocked_count))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main_bp.route('/stats.csv')
def stats_csv():
    links = link_service.get_links_stats()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'url', 'click_count', 'bot_click_count', 'light_clicks', 'dark_clicks', 'high_contrast_clicks', 'system_theme_clicks', 'en_clicks', 'de_clicks'])
    
    for link in links:
        writer.writerow([link['name'], link['url'], link['click_count'], link['bot_click_count'], 
                        link['light_clicks'], link['dark_clicks'], link['high_contrast_clicks'], link['system_theme_clicks'],
                        link['en_clicks'], link['de_clicks']])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=stats.csv'
    return response

@main_bp.route('/stats/blocklist.csv')
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
def stats_user_agents_csv():
    company_stats = link_service.get_user_agent_stats_by_company()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['company', 'count'])
    
    # Sort by count descending
    for company, count in sorted(company_stats.items(), key=lambda x: x[1], reverse=True):
        writer.writerow([company, count])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=user_agents.csv'
    return response

@main_bp.route('/about')
def about():
    from app.services.about_content import load_about_content
    lang = session.get('lang', 'en')
    about_content = load_about_content(lang)
    return render_template('about.html', about_content=about_content)

@main_bp.route('/privacy')
@main_bp.route('/datenschutz')
def privacy():
    """Privacy policy page with tool-specific privacy information."""
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
    return render_template('accessibility_statement.html')

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
