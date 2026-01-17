from flask import Blueprint, render_template, request, jsonify, Response
import json
import os
from datetime import datetime

from app.services.holiday_service import HolidayService, SUPPORTED_COUNTRIES
from app.services.calendar_pdf_service import CalendarPDFService
from app.services.link_service import increment_click_count

holiday_calendar_bp = Blueprint('holiday_calendar', __name__)

def load_tool_data():
    json_path = os.path.join(os.path.dirname(__file__), 'holiday_calendar_tool.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@holiday_calendar_bp.route('/tools/holidays')
def holiday_calendar():
    increment_click_count('/tools/holidays')
    
    tool_data = load_tool_data()
    countries = HolidayService.get_countries()
    
    # Get URL params for SEO text
    country_code = request.args.get('country', 'DE')
    region_code = request.args.get('region', '')
    year_param = request.args.get('year', '')
    view = request.args.get('view', '')
    
    # Only set year for SEO if explicitly provided (not "all") and valid
    # In calendar view, year is always shown; in list view, only when a specific year is selected
    year = None
    if year_param and year_param != 'all':
        try:
            year = int(year_param)
        except ValueError:
            year = None
    elif view == 'calendar' and not year_param:
        # Default to current year for calendar view if no year specified
        year = datetime.now().year
    
    # Get country and region names for SEO
    country_info = SUPPORTED_COUNTRIES.get(country_code, {'name': 'Deutschland', 'name_en': 'Germany'})
    country_name = country_info['name']
    country_name_en = country_info['name_en']
    
    region_name = ''
    region_name_en = ''
    if region_code:
        subdivisions = HolidayService.get_subdivisions(country_code)
        for sub in subdivisions:
            if sub.get('code') == region_code:
                # Name can be a list of {language, text} dicts or a string
                name_data = sub.get('name', sub.get('shortName', ''))
                if isinstance(name_data, list):
                    # Extract text from language list
                    for n in name_data:
                        if n.get('language') == 'DE':
                            region_name = n.get('text', '')
                        if n.get('language') == 'EN':
                            region_name_en = n.get('text', '')
                    if not region_name:
                        region_name = name_data[0].get('text', '') if name_data else ''
                    if not region_name_en:
                        region_name_en = region_name
                else:
                    region_name = name_data
                    region_name_en = name_data
                break
    
    return render_template('tools/holiday_calendar.html', 
                         tool_data=tool_data,
                         countries=countries,
                         seo_country=country_name,
                         seo_country_en=country_name_en,
                         seo_region=region_name,
                         seo_region_en=region_name_en,
                         seo_year=year)

@holiday_calendar_bp.route('/api/holidays/countries')
def api_countries():
    return jsonify(HolidayService.get_countries())

@holiday_calendar_bp.route('/api/holidays/subdivisions')
def api_subdivisions():
    country = request.args.get('country', 'DE')
    subdivisions = HolidayService.get_subdivisions(country)
    return jsonify(subdivisions)

@holiday_calendar_bp.route('/api/holidays')
def api_holidays():
    country = request.args.get('country', 'DE')
    subdivision = request.args.get('subdivision', 'all')
    include_past = request.args.get('include_past', 'false').lower() == 'true'
    lang = request.args.get('lang', 'DE').upper()
    if lang not in ['DE', 'EN', 'FR']:
        lang = 'DE'
    
    holidays = HolidayService.get_holidays(country, subdivision, include_past, lang)
    
    return jsonify({
        'success': True,
        'holidays': holidays,
        'count': len(holidays)
    })

@holiday_calendar_bp.route('/api/holidays/ical')
def api_holidays_ical():
    country = request.args.get('country', 'DE')
    subdivision = request.args.get('subdivision', 'all')
    
    # Generate iCal dynamically (prevents hotlinking)
    ical_content = HolidayService.generate_ical(country, subdivision if subdivision != 'all' else None)
    
    # Create filename
    if subdivision and subdivision != 'all':
        filename = f"holidays_{country.lower()}_{subdivision.lower().replace('-', '_')}.ics"
    else:
        filename = f"holidays_{country.lower()}.ics"
    
    return Response(
        ical_content,
        mimetype='text/calendar',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'text/calendar; charset=utf-8'
        }
    )

@holiday_calendar_bp.route('/api/holidays/pdf')
def api_holidays_pdf():
    country = request.args.get('country', 'DE')
    subdivision = request.args.get('subdivision', 'all')
    year = request.args.get('year')
    lang = request.args.get('lang', 'DE').upper()
    
    if lang not in ['DE', 'EN', 'FR', 'ES', 'IT']:
        lang = 'DE'
    
    try:
        year = int(year) if year else None
    except ValueError:
        year = None
    
    pdf_buffer = CalendarPDFService.generate_pdf(
        country, 
        subdivision if subdivision != 'all' else None,
        year,
        lang
    )
    
    # Create filename
    year_str = year if year else 'calendar'
    if subdivision and subdivision != 'all':
        filename = f"kalender_{year_str}_{country.lower()}_{subdivision.lower().replace('-', '_')}.pdf"
    else:
        filename = f"kalender_{year_str}_{country.lower()}.pdf"
    
    return Response(
        pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'application/pdf'
        }
    )


def get_sitemap_entries():
    """Provide sitemap entries for the holiday calendar tool."""
    current_year = datetime.now().year
    years = list(range(current_year, current_year + 6))
    
    entries = []
    
    for country_code, country_info in SUPPORTED_COUNTRIES.items():
        # Country-level entry
        country_name = country_info['name']
        
        # Get subdivisions
        subdivisions = HolidayService.get_subdivisions(country_code)
        
        # Create a section for this country
        country_section = {
            'title': country_name,
            'title_en': country_info['name_en'],
            'links': []
        }
        
        # Add year links for country
        for year in years:
            country_section['links'].append({
                'url': f'/tools/holidays?country={country_code}&year={year}&view=calendar',
                'label': f'{country_name} {year}',
                'label_en': f'{country_info["name_en"]} {year}'
            })
        
        # Add subdivision links
        for sub in subdivisions:
            sub_code = sub.get('code', '')
            name_data = sub.get('name', sub.get('shortName', ''))
            
            # Extract name from language/text list format
            sub_name = ''
            sub_name_en = ''
            if isinstance(name_data, list):
                for n in name_data:
                    if n.get('language') == 'DE':
                        sub_name = n.get('text', '')
                    if n.get('language') == 'EN':
                        sub_name_en = n.get('text', '')
                if not sub_name:
                    sub_name = name_data[0].get('text', '') if name_data else ''
                if not sub_name_en:
                    sub_name_en = sub_name
            else:
                sub_name = name_data
                sub_name_en = name_data
            
            for year in years:
                country_section['links'].append({
                    'url': f'/tools/holidays?country={country_code}&region={sub_code}&year={year}&view=calendar',
                    'label': f'{sub_name} {year}',
                    'label_en': f'{sub_name_en} {year}'
                })
        
        entries.append(country_section)
    
    # Sort by German name
    entries.sort(key=lambda x: x['title'])
    
    return {
        'tool_name': 'Feiertagskalender',
        'tool_name_en': 'Holiday Calendar',
        'tool_url': '/tools/holidays',
        'sections': entries
    }
