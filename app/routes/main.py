from flask import Blueprint, render_template, request, make_response, jsonify, session, Response
from app import db
import csv
import io
from datetime import datetime
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
    links = link_service.get_links_stats()
    return render_template('stats.html', links=links)

@main_bp.route('/stats.csv')
def stats_csv():
    links = link_service.get_links_stats()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'url', 'click_count'])
    
    for link in links:
        writer.writerow([link['name'], link['url'], link['click_count']])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=stats.csv'
    return response

@main_bp.route('/sitemaps/index.xml')
def sitemap_xml():
    """XML sitemap for search engines."""
    from app.models import Link
    
    base_url = 'https://lotsof.tools'
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Start XML
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    # Static pages
    static_pages = [
        ('/', '1.0', 'daily'),
        ('/about', '0.5', 'monthly'),
        ('/privacy', '0.3', 'monthly'),
    ]
    
    for url, priority, changefreq in static_pages:
        xml_parts.append(f'''  <url>
    <loc>{base_url}{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>''')
    
    # All tools
    links = Link.query.all()
    for link in links:
        xml_parts.append(f'''  <url>
    <loc>{base_url}{link.url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')
    
    xml_parts.append('</urlset>')
    
    xml_content = '\n'.join(xml_parts)
    return Response(xml_content, mimetype='application/xml')

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
