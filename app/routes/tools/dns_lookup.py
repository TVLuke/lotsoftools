from flask import Blueprint, render_template, request, jsonify
import dns.resolver
import dns.reversename
import json
import os
from datetime import datetime
from app.services.link_service import increment_click_count

dns_lookup_bp = Blueprint('dns_lookup', __name__, url_prefix='/tools')

# Default DNS servers to query
DEFAULT_DNS_SERVERS = [
    {'name': 'Google', 'ip': '8.8.8.8'},
    {'name': 'Cloudflare', 'ip': '1.1.1.1'},
    {'name': 'Quad9', 'ip': '9.9.9.9'},
]

# Supported record types (common ones that dnspython supports)
RECORD_TYPES = [
    'A', 'AAAA', 'AFSDB', 'APL', 'CAA', 'CDNSKEY', 'CDS', 'CERT', 'CNAME', 
    'CSYNC', 'DHCID', 'DLV', 'DNAME', 'DNSKEY', 'DS', 'EUI48', 'EUI64',
    'HINFO', 'HIP', 'HTTPS', 'IPSECKEY', 'KEY', 'KX', 'LOC', 'MX', 'NAPTR',
    'NS', 'NSEC', 'NSEC3', 'NSEC3PARAM', 'OPENPGPKEY', 'PTR', 'RP', 'RRSIG',
    'SIG', 'SMIMEA', 'SOA', 'SRV', 'SSHFP', 'SVCB', 'TLSA', 'TSIG', 'TXT',
    'URI', 'ZONEMD'
]

@dns_lookup_bp.route('/dns-lookup')
def index():
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'dns_lookup_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/dns_lookup.html', 
                           tool_data=tool_data,
                           dns_servers=DEFAULT_DNS_SERVERS,
                           record_types=RECORD_TYPES)

def check_email_auth(resolver, domain):
    """Check SPF and DMARC records for email authentication analysis."""
    email_auth = {
        'spf': None,
        'dmarc': None
    }
    
    # Check SPF (TXT record on domain starting with v=spf1)
    try:
        answers = resolver.resolve(domain, 'TXT')
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if txt.startswith('v=spf1'):
                email_auth['spf'] = {
                    'found': True,
                    'record': txt,
                    'valid': True
                }
                break
        if not email_auth['spf']:
            email_auth['spf'] = {'found': False, 'record': None}
    except Exception:
        email_auth['spf'] = {'found': False, 'record': None}
    
    # Check DMARC (TXT record at _dmarc.domain)
    try:
        dmarc_domain = f'_dmarc.{domain}'
        answers = resolver.resolve(dmarc_domain, 'TXT')
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if txt.startswith('v=DMARC1'):
                # Parse DMARC policy
                policy = None
                if 'p=reject' in txt:
                    policy = 'reject'
                elif 'p=quarantine' in txt:
                    policy = 'quarantine'
                elif 'p=none' in txt:
                    policy = 'none'
                
                email_auth['dmarc'] = {
                    'found': True,
                    'record': txt,
                    'policy': policy
                }
                break
        if not email_auth['dmarc']:
            email_auth['dmarc'] = {'found': False, 'record': None}
    except Exception:
        email_auth['dmarc'] = {'found': False, 'record': None}
    
    return email_auth

@dns_lookup_bp.route('/dns-lookup/query', methods=['POST'])
def query_dns():
    data = request.get_json()
    domain = data.get('domain', '').strip()
    record_type = data.get('record_type', 'ALL')
    custom_server = data.get('custom_server', '').strip()
    
    if not domain:
        return jsonify({'error': 'Domain is required'}), 400
    
    # Build list of servers to query
    servers = DEFAULT_DNS_SERVERS.copy()
    if custom_server:
        servers.append({'name': 'Custom', 'ip': custom_server})
    
    # Determine which record types to query
    if record_type == 'ALL':
        types_to_query = RECORD_TYPES
    else:
        types_to_query = [record_type]
    
    # Check if we should include email auth info
    check_email = record_type == 'ALL' or record_type == 'MX'
    
    results = {
        'domain': domain,
        'timestamp': datetime.now().isoformat(),
        'record_type': record_type,
        'servers': []
    }
    
    for server in servers:
        server_result = {
            'name': server['name'],
            'ip': server['ip'],
            'records': {}
        }
        
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [server['ip']]
        resolver.timeout = 5
        resolver.lifetime = 5
        
        for rtype in types_to_query:
            try:
                answers = resolver.resolve(domain, rtype)
                records = []
                for rdata in answers:
                    record_data = {'value': rdata.to_text()}
                    
                    # Add extra info for specific record types
                    if rtype == 'MX':
                        record_data['preference'] = rdata.preference
                        record_data['exchange'] = str(rdata.exchange)
                    elif rtype == 'SOA':
                        record_data['mname'] = str(rdata.mname)
                        record_data['rname'] = str(rdata.rname)
                        record_data['serial'] = rdata.serial
                        record_data['refresh'] = rdata.refresh
                        record_data['retry'] = rdata.retry
                        record_data['expire'] = rdata.expire
                        record_data['minimum'] = rdata.minimum
                    elif rtype == 'SRV':
                        record_data['priority'] = rdata.priority
                        record_data['weight'] = rdata.weight
                        record_data['port'] = rdata.port
                        record_data['target'] = str(rdata.target)
                    
                    records.append(record_data)
                
                server_result['records'][rtype] = {
                    'success': True,
                    'data': records,
                    'ttl': answers.rrset.ttl if answers.rrset else None
                }
            except dns.resolver.NXDOMAIN:
                server_result['records'][rtype] = {
                    'success': False,
                    'error': 'NXDOMAIN',
                    'message': 'Domain does not exist'
                }
            except dns.resolver.NoAnswer:
                server_result['records'][rtype] = {
                    'success': False,
                    'error': 'NoAnswer',
                    'message': 'No records of this type'
                }
            except dns.resolver.NoNameservers:
                server_result['records'][rtype] = {
                    'success': False,
                    'error': 'NoNameservers',
                    'message': 'No nameservers available'
                }
            except dns.exception.Timeout:
                server_result['records'][rtype] = {
                    'success': False,
                    'error': 'Timeout',
                    'message': 'Query timed out'
                }
            except Exception as e:
                server_result['records'][rtype] = {
                    'success': False,
                    'error': 'Error',
                    'message': str(e)
                }
        
        # Add email authentication info if MX was queried
        if check_email:
            server_result['email_auth'] = check_email_auth(resolver, domain)
        
        results['servers'].append(server_result)
    
    return jsonify(results)
