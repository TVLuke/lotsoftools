import os
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

# Cache for subdomain routes
_subdomain_routes_cache = None

def _get_subdomain_routes():
    """Load subdomain mappings from tool JSON files."""
    global _subdomain_routes_cache
    if _subdomain_routes_cache is not None:
        return _subdomain_routes_cache
    
    import json
    import glob
    
    routes = {}
    tools_dir = os.path.join(os.path.dirname(__file__), 'routes', 'tools')
    for json_file in glob.glob(os.path.join(tools_dir, '*_tool.json')):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if 'subdomain' in data and 'route' in data:
                    subdomains = data['subdomain']
                    if isinstance(subdomains, str):
                        subdomains = [subdomains]
                    for subdomain in subdomains:
                        routes[subdomain] = data['route']
        except (json.JSONDecodeError, IOError):
            pass
    
    _subdomain_routes_cache = routes
    return routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    os.makedirs('data', exist_ok=True)
    
    @app.before_request
    def set_language():
        if 'lang' not in session:
            session['lang'] = request.accept_languages.best_match(['en', 'de']) or 'en'
    
    @app.before_request
    def handle_subdomain_redirect():
        from flask import redirect
        host = request.host.split(':')[0]  # Remove port if present
        
        # Check if this is a subdomain request (not www, not bare domain)
        parts = host.split('.')
        if len(parts) >= 3 and parts[0] not in ('www', ''):
            subdomain = parts[0]
            # Load subdomain mappings from tool JSON files
            subdomain_routes = _get_subdomain_routes()
            if subdomain in subdomain_routes:
                # Build the main domain (remove subdomain)
                main_domain = '.'.join(parts[1:])
                scheme = 'https' if request.is_secure else 'http'
                
                # Redirect to the main domain with tool route
                target = f"{scheme}://{main_domain}{subdomain_routes[subdomain]}"
                if request.query_string:
                    target += '?' + request.query_string.decode('utf-8')
                return redirect(target, code=301)
    
    @app.context_processor
    def inject_language():
        return {'current_lang': session.get('lang', 'en')}

    @app.context_processor
    def inject_support_links():
        from app.services.support_links import (
            load_support_links,
            support_icon_class,
            support_placement_enabled,
            support_link_text,
        )
        return {
            'support_links': load_support_links(),
            'support_icon_class': support_icon_class,
            'support_placement_enabled': support_placement_enabled,
            'support_link_text': support_link_text,
        }
    
    def sync_app_data():
        from app.utils import init_tools
        init_tools()
    
    from app.routes.main import main_bp
    from app.routes.sitemaps import sitemaps_bp
    from app.routes.tools.letter_counter import letter_counter_bp
    from app.routes.tools.json_formatter import json_formatter_bp
    from app.routes.tools.xml_formatter import xml_formatter_bp
    from app.routes.tools.yaml_formatter import yaml_formatter_bp
    from app.routes.tools.csv_table import csv_table_bp
    from app.routes.tools.qr_generator import qr_generator_bp
    from app.routes.tools.uuid_generator import uuid_generator_bp
    from app.routes.tools.random_string import random_string_bp
    from app.routes.tools.color import color_bp
    from app.routes.tools.colorblind import colorblind_bp
    from app.routes.tools.calendar import calendar_bp
    from app.routes.tools.hash_generator import hash_generator_bp
    from app.routes.tools.iban_validator import iban_validator_bp
    from app.routes.tools.base_converter import base_converter_bp
    from app.routes.tools.barcode_generator import barcode_generator_bp
    from app.routes.tools.unit_converter import unit_converter_bp
    from app.routes.tools.favicon_generator import favicon_generator_bp
    from app.routes.tools.ip_lookup import ip_lookup_bp
    from app.routes.tools.emoji_search import emoji_search_bp
    from app.routes.tools.lorem_ipsum import lorem_ipsum_bp
    from app.routes.tools.icon_finder import icon_finder_bp
    from app.routes.tools.subtitle_converter import subtitle_converter_bp
    from app.routes.tools.image_cropper import image_cropper_bp
    from app.routes.tools.speed_test import speed_test_bp
    from app.routes.tools.youtube_dl import youtube_dl_bp
    from app.routes.tools.dns_lookup import dns_lookup_bp
    from app.routes.tools.diff_tool import diff_tool_bp
    from app.routes.tools.holiday_calendar import holiday_calendar_bp
    from app.routes.tools.date_calculator import date_calculator_bp
    from app.routes.tools.noise_generator import noise_generator_bp
    from app.routes.tools.clock import clock_bp
    from app.routes.tools.base64_converter import base64_bp
    from app.routes.tools.ascii_table import ascii_table_bp
    from app.routes.tools.coordinate_converter import coordinate_converter_bp
    from app.routes.tools.teleprompter import teleprompter_bp
    from app.routes.tools.lastfm_export import lastfm_export_bp
    from app.routes.tools.distance import distance_bp
    from app.routes.tools.radius import radius_bp
    from app.routes.tools.map_tracer import map_tracer_bp
    from app.routes.tools.simulate_location import simulate_location_bp
    from app.routes.tools.dice import dice_bp
    from app.routes.tools.map_maker import map_maker_bp
    from app.routes.icon_cache import icon_cache_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(sitemaps_bp)
    app.register_blueprint(letter_counter_bp)
    app.register_blueprint(json_formatter_bp)
    app.register_blueprint(xml_formatter_bp)
    app.register_blueprint(yaml_formatter_bp)
    app.register_blueprint(csv_table_bp)
    app.register_blueprint(qr_generator_bp)
    app.register_blueprint(uuid_generator_bp)
    app.register_blueprint(random_string_bp)
    app.register_blueprint(color_bp)
    app.register_blueprint(colorblind_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(hash_generator_bp)
    app.register_blueprint(iban_validator_bp)
    app.register_blueprint(base_converter_bp)
    app.register_blueprint(barcode_generator_bp)
    app.register_blueprint(unit_converter_bp)
    app.register_blueprint(favicon_generator_bp)
    app.register_blueprint(ip_lookup_bp)
    app.register_blueprint(emoji_search_bp)
    app.register_blueprint(lorem_ipsum_bp)
    app.register_blueprint(icon_finder_bp)
    app.register_blueprint(subtitle_converter_bp)
    app.register_blueprint(image_cropper_bp)
    app.register_blueprint(speed_test_bp)
    app.register_blueprint(youtube_dl_bp)
    app.register_blueprint(dns_lookup_bp)
    app.register_blueprint(diff_tool_bp)
    app.register_blueprint(holiday_calendar_bp)
    app.register_blueprint(date_calculator_bp)
    app.register_blueprint(noise_generator_bp)
    app.register_blueprint(clock_bp)
    app.register_blueprint(base64_bp)
    app.register_blueprint(ascii_table_bp)
    app.register_blueprint(coordinate_converter_bp)
    app.register_blueprint(teleprompter_bp)
    app.register_blueprint(lastfm_export_bp)
    app.register_blueprint(distance_bp)
    app.register_blueprint(radius_bp)
    app.register_blueprint(map_tracer_bp)
    app.register_blueprint(simulate_location_bp)
    app.register_blueprint(dice_bp)
    app.register_blueprint(map_maker_bp)
    app.register_blueprint(icon_cache_bp)
    
    with app.app_context():
        # Import models so SQLAlchemy knows about them
        from app.models.link import Link
        
        # Create database tables if they don't exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.has_table('link'):
            db.create_all()
        
        sync_app_data()
        
        # Download vendor libraries if missing
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(app.root_path), 'scripts'))
        from download_vendor_libs import download_vendor_libs
        if download_vendor_libs(silent=True):
            print("✓ Downloaded missing vendor libraries")
        
        # Initialize holiday service (fetches from API or loads cache)
        # Use data directory which is mounted as a volume for persistence
        from app.services.holiday_service import HolidayService
        holidays_dir = os.path.join(os.path.dirname(app.root_path), 'data', 'holidays')
        HolidayService.init(holidays_dir)
    
    return app
