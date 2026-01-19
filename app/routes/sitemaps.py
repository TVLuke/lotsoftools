from flask import Blueprint, Response, session
from datetime import datetime

sitemaps_bp = Blueprint('sitemaps', __name__)

@sitemaps_bp.route('/sitemaps/index.xml')
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

@sitemaps_bp.route('/sitemaps/extra-pages.xml')
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

@sitemaps_bp.route('/sitemaps/products.xml')
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

@sitemaps_bp.route('/sitemaps/categories.xml')
def sitemap_categories_xml():
    """Sitemap for category/tag pages - currently empty as no dedicated category pages exist."""
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '</urlset>'
    ]
    return Response('\n'.join(xml_parts), mimetype='application/xml')

@sitemaps_bp.route('/rss/products.rss')
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
