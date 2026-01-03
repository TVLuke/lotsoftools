from flask import Blueprint, render_template, request, jsonify
import json
import os
import geoip2.database
from ipaddress import ip_address, IPv4Address, IPv6Address
from app.utils.geoip_downloader import ensure_geoip_databases, GEOIP_DIR, CITY_DB_PATH, ASN_DB_PATH
from app.services.link_service import increment_click_count

ip_lookup_bp = Blueprint('ip_lookup', __name__, url_prefix='/tools')

# Ensure databases are downloaded on module import
ensure_geoip_databases()

def get_client_ip():
    """Get the client's real IP address, considering proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

@ip_lookup_bp.route('/ip-lookup')
def index():
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'ip_lookup_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    # Get client's IP for auto-detection
    client_ip = get_client_ip()
    
    return render_template('tools/ip_lookup.html', tool_data=tool_data, client_ip=client_ip)

@ip_lookup_bp.route('/ip-lookup/query', methods=['POST'])
def query():
    data = request.get_json()
    ip = data.get('ip', '').strip()
    
    if not ip:
        return jsonify({'error': 'No IP address provided'}), 400
    
    # Validate IP address
    try:
        ip_obj = ip_address(ip)
    except ValueError:
        return jsonify({'error': 'Invalid IP address format'}), 400
    
    result = {
        'ip': ip,
        'version': 'IPv4' if isinstance(ip_obj, IPv4Address) else 'IPv6'
    }
    
    # Check if databases exist
    if not os.path.exists(CITY_DB_PATH):
        return jsonify({
            'error': 'GeoLite2 database not found. Please download GeoLite2-City.mmdb and place it in the geoip_data directory.'
        }), 500
    
    try:
        # Get city/location data
        with geoip2.database.Reader(CITY_DB_PATH) as city_reader:
            try:
                city_response = city_reader.city(ip)
                
                result['country'] = {
                    'name': city_response.country.name,
                    'code': city_response.country.iso_code
                }
                
                if city_response.subdivisions.most_specific.name:
                    result['region'] = city_response.subdivisions.most_specific.name
                
                if city_response.city.name:
                    result['city'] = city_response.city.name
                
                if city_response.postal.code:
                    result['postal_code'] = city_response.postal.code
                
                if city_response.location.latitude and city_response.location.longitude:
                    result['location'] = {
                        'latitude': city_response.location.latitude,
                        'longitude': city_response.location.longitude,
                        'accuracy_radius': city_response.location.accuracy_radius,
                        'time_zone': city_response.location.time_zone
                    }
                
            except geoip2.errors.AddressNotFoundError:
                result['city_error'] = 'Location data not found for this IP'
        
        # Get ASN/ISP data
        if os.path.exists(ASN_DB_PATH):
            with geoip2.database.Reader(ASN_DB_PATH) as asn_reader:
                try:
                    asn_response = asn_reader.asn(ip)
                    result['asn'] = {
                        'number': asn_response.autonomous_system_number,
                        'organization': asn_response.autonomous_system_organization
                    }
                except geoip2.errors.AddressNotFoundError:
                    result['asn_error'] = 'ASN data not found for this IP'
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Lookup failed: {str(e)}'}), 500

@ip_lookup_bp.route('/ip-lookup/my-ip')
def my_ip():
    """Return the client's IP address"""
    client_ip = get_client_ip()
    return jsonify({'ip': client_ip})
