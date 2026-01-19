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
    user_agents = link_service.get_user_agent_stats()
    bot_user_agents = link_service.get_bot_user_agents()
    human_user_agents = link_service.get_human_user_agents()
    server_start_time = link_service.get_server_start_time()
    return render_template('stats.html', links=links, user_agents=user_agents, 
                          bot_user_agents=bot_user_agents, human_user_agents=human_user_agents,
                          server_start_time=server_start_time)

@main_bp.route('/stats.csv')
def stats_csv():
    links = link_service.get_links_stats()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'url', 'click_count', 'bot_click_count'])
    
    for link in links:
        writer.writerow([link['name'], link['url'], link['click_count'], link['bot_click_count']])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=stats.csv'
    return response

@main_bp.route('/sitemaps/index.xml')
def sitemap_index_xml():
    """Sitemap index pointing to other sitemaps."""
    base_url = 'https://lotsof.tools'
    today = datetime.now().strftime('%Y-%m-%d')
    
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <sitemap><loc>{base_url}/sitemaps/extra-pages.xml</loc><lastmod>{today}</lastmod></sitemap>',
        f'  <sitemap><loc>{base_url}/sitemaps/products.xml</loc><lastmod>{today}</lastmod></sitemap>',
        f'  <sitemap><loc>{base_url}/sitemaps/categories.xml</loc><lastmod>{today}</lastmod></sitemap>',
        '</sitemapindex>'
    ]
    
    return Response('\n'.join(xml_parts), mimetype='application/xml')

@main_bp.route('/sitemaps/extra-pages.xml')
def sitemap_extra_pages_xml():
    """Sitemap for static/extra pages."""
    base_url = 'https://lotsof.tools'
    today = datetime.now().strftime('%Y-%m-%d')
    
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    static_pages = [
        ('/', '1.0', 'daily'),
        ('/about', '0.5', 'monthly'),
        ('/privacy', '0.3', 'monthly'),
        ('/sitemap', '0.4', 'weekly'),
        ('/stats', '0.3', 'daily'),
    ]
    
    for url, priority, changefreq in static_pages:
        xml_parts.append(f'''  <url>
    <loc>{base_url}{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>''')
    
    xml_parts.append('</urlset>')
    return Response('\n'.join(xml_parts), mimetype='application/xml')

@main_bp.route('/sitemaps/products.xml')
def sitemap_products_xml():
    """Sitemap for all tools (products)."""
    from app.models import Link
    
    base_url = 'https://lotsof.tools'
    today = datetime.now().strftime('%Y-%m-%d')
    
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    links = Link.query.all()
    for link in links:
        xml_parts.append(f'''  <url>
    <loc>{base_url}{link.url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')
    
    xml_parts.append('</urlset>')
    return Response('\n'.join(xml_parts), mimetype='application/xml')

@main_bp.route('/sitemaps/categories.xml')
def sitemap_categories_xml():
    """Sitemap for category/tag pages."""
    base_url = 'https://lotsof.tools'
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get unique tags from all tools
    from app.models import Link
    tags = set()
    for link in Link.query.all():
        if link.tags:
            for tag in link.tags:
                tags.add(tag)
    
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    # Category pages based on tags (if we have tag filter pages)
    # For now, list the main page with tag anchors
    for tag in sorted(tags):
        xml_parts.append(f'''  <url>
    <loc>{base_url}/?tag={tag}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>''')
    
    xml_parts.append('</urlset>')
    return Response('\n'.join(xml_parts), mimetype='application/xml')

@main_bp.route('/rss/products.rss')
def rss_products():
    """RSS feed of all tools."""
    from app.models import Link
    
    base_url = 'https://lotsof.tools'
    lang = session.get('lang', 'en')
    now = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    rss_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        '<channel>',
        '  <title>Lots of Tools</title>',
        f'  <link>{base_url}</link>',
        '  <description>Free online tools for developers and everyday use</description>',
        '  <language>en</language>',
        f'  <lastBuildDate>{now}</lastBuildDate>',
        f'  <atom:link href="{base_url}/rss/products.rss" rel="self" type="application/rss+xml"/>',
    ]
    
    links = Link.query.order_by(Link.id.desc()).all()
    for link in links:
        name = link.get_name(lang)
        desc = link.get_description(lang) or name
        rss_parts.append(f'''  <item>
    <title>{name}</title>
    <link>{base_url}{link.url}</link>
    <description>{desc}</description>
    <guid>{base_url}{link.url}</guid>
  </item>''')
    
    rss_parts.append('</channel>')
    rss_parts.append('</rss>')
    
    return Response('\n'.join(rss_parts), mimetype='application/rss+xml')

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
