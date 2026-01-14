from flask import Blueprint, render_template, request, make_response, jsonify, session
from app import db
from app.services import link_service

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
        return jsonify({'success': True, 'language': lang})
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
    from app.models import Link
    links = Link.query.order_by(Link.click_count.desc()).all()
    return render_template('stats.html', links=links)

@main_bp.route('/about')
def about():
    return render_template('about.html')

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
