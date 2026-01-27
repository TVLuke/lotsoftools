#!/usr/bin/env python3
"""
Download vendor libraries and calculate SRI hashes for local hosting.
"""

import hashlib
import base64
import os
import urllib.request
import ssl
import json
from datetime import datetime

LIBS_DIR = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'libs', 'vendor')
METADATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'libraries.json')

# URLs taken EXACTLY from app/templates/components/imports/*.html
# Each library includes metadata for the third-party libraries page
LIBRARIES = [
    {
        'name': 'bootstrap',
        'display_name': 'Bootstrap',
        'version': '5.3.0',
        'license': 'MIT',
        'github': 'twbs/bootstrap',
        'homepage': 'https://getbootstrap.com',
        'license_url': 'https://raw.githubusercontent.com/twbs/bootstrap/v5.3.0/LICENSE',
        'files': [
            {
                'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
                'filename': 'bootstrap.min.css'
            },
            {
                'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
                'filename': 'bootstrap.bundle.min.js'
            }
        ]
    },
    {
        'name': 'fontawesome',
        'display_name': 'Font Awesome',
        'version': '6.4.0',
        'license': 'Font Awesome Free License',
        'github': 'FortAwesome/Font-Awesome',
        'homepage': 'https://fontawesome.com',
        'license_url': 'https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/LICENSE.txt',
        'files': [
            {
                'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
                'filename': 'all.min.css'
            }
        ],
        'extra_files': [
            # Webfonts - CSS references ../webfonts/ so these go in a sibling folder
            {'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2', 'filename': 'fa-brands-400.woff2', 'subdir': '../webfonts'},
            {'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.ttf', 'filename': 'fa-brands-400.ttf', 'subdir': '../webfonts'},
            {'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2', 'filename': 'fa-regular-400.woff2', 'subdir': '../webfonts'},
            {'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.ttf', 'filename': 'fa-regular-400.ttf', 'subdir': '../webfonts'},
            {'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2', 'filename': 'fa-solid-900.woff2', 'subdir': '../webfonts'},
            {'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.ttf', 'filename': 'fa-solid-900.ttf', 'subdir': '../webfonts'},
            {'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-v4compatibility.woff2', 'filename': 'fa-v4compatibility.woff2', 'subdir': '../webfonts'},
            {'url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-v4compatibility.ttf', 'filename': 'fa-v4compatibility.ttf', 'subdir': '../webfonts'},
        ]
    },
    {
        'name': 'jquery',
        'display_name': 'jQuery',
        'version': '3.7.0',
        'license': 'MIT',
        'github': 'jquery/jquery',
        'homepage': 'https://jquery.com',
        'license_url': 'https://raw.githubusercontent.com/jquery/jquery/3.7.0/LICENSE.txt',
        'files': [
            {
                'url': 'https://code.jquery.com/jquery-3.7.0.min.js',
                'filename': 'jquery-3.7.0.min.js'
            }
        ]
    },
    {
        'name': 'js-yaml',
        'display_name': 'js-yaml',
        'version': '4.1.0',
        'license': 'MIT',
        'github': 'nodeca/js-yaml',
        'homepage': 'https://github.com/nodeca/js-yaml',
        'license_url': 'https://raw.githubusercontent.com/nodeca/js-yaml/4.1.0/LICENSE',
        'files': [
            {
                'url': 'https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js',
                'filename': 'js-yaml.min.js'
            }
        ]
    },
    {
        'name': 'qrcode',
        'display_name': 'QRCode.js',
        'version': '1.0.0',
        'license': 'MIT',
        'github': 'davidshimjs/qrcodejs',
        'homepage': 'https://github.com/davidshimjs/qrcodejs',
        'license_url': 'https://raw.githubusercontent.com/davidshimjs/qrcodejs/master/LICENSE',
        'files': [
            {
                'url': 'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js',
                'filename': 'qrcode.min.js'
            }
        ]
    },
    {
        'name': 'marked',
        'display_name': 'Marked',
        'version': 'latest',
        'license': 'MIT',
        'github': 'markedjs/marked',
        'homepage': 'https://marked.js.org',
        'license_url': 'https://raw.githubusercontent.com/markedjs/marked/master/LICENSE.md',
        'files': [
            {
                'url': 'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
                'filename': 'marked.min.js'
            }
        ]
    },
    {
        'name': 'colorblind',
        'display_name': '@bjornlu/colorblind',
        'version': 'latest',
        'license': 'MIT',
        'github': 'bluwy/colorblind',
        'homepage': 'https://github.com/bluwy/colorblind',
        'license_url': 'https://raw.githubusercontent.com/bluwy/colorblind/master/LICENSE',
        'files': [
            {
                'url': 'https://cdn.jsdelivr.net/npm/@bjornlu/colorblind',
                'filename': 'colorblind.js'
            }
        ]
    },
    {
        'name': 'html2canvas',
        'display_name': 'html2canvas',
        'version': '1.4.1',
        'license': 'MIT',
        'github': 'niklasvh/html2canvas',
        'homepage': 'https://html2canvas.hertzen.com',
        'license_url': 'https://raw.githubusercontent.com/niklasvh/html2canvas/v1.4.1/LICENSE',
        'files': [
            {
                'url': 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js',
                'filename': 'html2canvas.min.js'
            }
        ]
    },
    {
        'name': 'convert',
        'display_name': 'convert',
        'version': '5.x',
        'license': 'MIT',
        'github': 'jonahsnider/convert',
        'homepage': 'https://convert.js.org',
        'license_url': 'https://raw.githubusercontent.com/jonahsnider/convert/main/license.md',
        'files': [
            {
                'url': 'https://cdn.jsdelivr.net/npm/convert@5/dist/index.js',
                'filename': 'convert.min.js'
            }
        ]
    },
    {
        'name': 'leaflet',
        'display_name': 'Leaflet',
        'version': '1.9.4',
        'license': 'BSD-2-Clause',
        'github': 'Leaflet/Leaflet',
        'homepage': 'https://leafletjs.com',
        'license_url': 'https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/LICENSE',
        'files': [
            {
                'url': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
                'filename': 'leaflet.css'
            },
            {
                'url': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
                'filename': 'leaflet.js'
            }
        ],
        'extra_files': [
            {'url': 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png', 'filename': 'marker-icon.png', 'subdir': 'images'},
            {'url': 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png', 'filename': 'marker-icon-2x.png', 'subdir': 'images'},
            {'url': 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png', 'filename': 'marker-shadow.png', 'subdir': 'images'},
        ]
    },
    {
        'name': 'highlightjs',
        'display_name': 'highlight.js',
        'version': '11.11.1',
        'license': 'BSD-3-Clause',
        'github': 'highlightjs/highlight.js',
        'homepage': 'https://highlightjs.org',
        'license_url': 'https://raw.githubusercontent.com/highlightjs/highlight.js/11.11.1/LICENSE',
        'files': [
            {
                'url': 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/styles/default.min.css',
                'filename': 'default.min.css'
            },
            {
                'url': 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/highlight.min.js',
                'filename': 'highlight.min.js'
            }
        ]
    },
    {
        'name': 'dojo',
        'display_name': 'Dojo Toolkit',
        'version': '1.14.1',
        'license': 'BSD-3-Clause OR AFL-2.1',
        'github': 'dojo/dojo',
        'homepage': 'https://dojotoolkit.org',
        'license_url': 'https://raw.githubusercontent.com/dojo/dojo/1.14.1/LICENSE',
        'files': [
            {
                'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dijit/themes/claro/claro.css',
                'filename': 'claro.css'
            },
            {
                'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/dojo.js',
                'filename': 'dojo.js'
            }
        ],
        'extra_files': [
            # Dojo AMD modules needed for dojox/color/Palette
            # dojo/_base modules
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/_base/array.js', 'filename': 'array.js', 'subdir': 'dojo/_base'},
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/_base/lang.js', 'filename': 'lang.js', 'subdir': 'dojo/_base'},
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/_base/kernel.js', 'filename': 'kernel.js', 'subdir': 'dojo/_base'},
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/_base/config.js', 'filename': 'config.js', 'subdir': 'dojo/_base'},
            # dojo core modules
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/has.js', 'filename': 'has.js', 'subdir': 'dojo'},
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/sniff.js', 'filename': 'sniff.js', 'subdir': 'dojo'},
            # dojox modules
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojox/main.js', 'filename': 'main.js', 'subdir': 'dojox'},
            # dojox/color modules
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojox/color/Palette.js', 'filename': 'Palette.js', 'subdir': 'dojox/color'},
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojox/color/_base.js', 'filename': '_base.js', 'subdir': 'dojox/color'},
            # dojo/colors needed by dojox/color
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/colors.js', 'filename': 'colors.js', 'subdir': 'dojo'},
            {'url': 'https://ajax.googleapis.com/ajax/libs/dojo/1.14.1/dojo/_base/Color.js', 'filename': 'Color.js', 'subdir': 'dojo/_base'},
        ]
    }
]

# Static libraries that are included in the repo (not downloaded)
STATIC_LIBRARIES = [
    {
        'name': 'analogclock',
        'display_name': 'Analog Clock',
        'version': '1.0.1',
        'license': 'MIT',
        'github': 'niconiahi/analogclock',
        'homepage': 'https://github.com/niconiahi/analogclock',
        'license_url': 'https://raw.githubusercontent.com/niconiahi/analogclock/master/LICENSE.txt',
    },
    {
        'name': 'uuid-js',
        'display_name': 'uuid-js',
        'version': '0.7.5',
        'license': 'Apache-2.0',
        'github': 'pnegri/uuid-js',
        'homepage': 'https://github.com/pnegri/uuid-js',
        'license_url': 'https://raw.githubusercontent.com/pnegri/uuid-js/master/LICENSE.txt',
    },
    {
        'name': 'lorem-json',
        'display_name': 'Lorem Ipsum JSON',
        'version': 'unknown',
        'license': 'MIT',
        'github': 'niconiahi/lorem-ipsum-json',
        'homepage': 'https://github.com/niconiahi/lorem-ipsum-json',
        'license_url': 'https://raw.githubusercontent.com/niconiahi/lorem-ipsum-json/master/LICENSE.txt',
        'note': 'Lorem Ipsum text data',
    },
    {
        'name': 'well-known-bots',
        'display_name': 'Well-Known Bots',
        'version': 'latest',
        'license': 'MIT',
        'github': 'monperrus/crawler-user-agents',
        'homepage': 'https://github.com/monperrus/crawler-user-agents',
        'license_url': 'https://raw.githubusercontent.com/monperrus/crawler-user-agents/master/LICENSE',
        'note': 'Bot detection database',
    },
    {
        'name': 'blocklist-project',
        'display_name': 'The Block List Project',
        'version': 'latest',
        'license': 'Unlicense (Public Domain)',
        'github': 'blocklistproject/Lists',
        'homepage': 'https://blocklistproject.github.io/Lists/',
        'license_url': 'https://raw.githubusercontent.com/blocklistproject/Lists/master/LICENSE',
        'note': 'Domain blocklists for malware, phishing, scams, etc.',
    },
]


def calculate_sri_hash(content: bytes) -> str:
    """Calculate SRI hash (SHA-384) for content."""
    sha384 = hashlib.sha384(content).digest()
    b64 = base64.b64encode(sha384).decode('ascii')
    return f"sha384-{b64}"


def download_file(url: str) -> bytes:
    """Download a file and return its content."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        return response.read()


def download_vendor_libs(silent=False):
    """Download vendor libraries. Returns True if any files were downloaded."""
    os.makedirs(LIBS_DIR, exist_ok=True)
    
    downloaded_any = False
    results = {}
    
    for lib in LIBRARIES:
        lib_dir = os.path.join(LIBS_DIR, lib['name'])
        os.makedirs(lib_dir, exist_ok=True)
        
        results[lib['name']] = {
            'files': []
        }
        
        for file_info in lib['files']:
            filepath = os.path.join(lib_dir, file_info['filename'])
            
            if os.path.exists(filepath):
                if not silent:
                    print(f"Already exists: {filepath}")
                with open(filepath, 'rb') as f:
                    content = f.read()
            else:
                downloaded_any = True
                if not silent:
                    print(f"Downloading: {file_info['url']}")
                content = download_file(file_info['url'])
                with open(filepath, 'wb') as f:
                    f.write(content)
                if not silent:
                    print(f"Saved to: {filepath}")
            
            sri_hash = calculate_sri_hash(content)
            relative_path = f"/static/libs/vendor/{lib['name']}/{file_info['filename']}"
            
            results[lib['name']]['files'].append({
                'filename': file_info['filename'],
                'path': relative_path,
                'integrity': sri_hash,
                'original_url': file_info['url']
            })
            
            if not silent:
                print(f"  SRI: {sri_hash}\n")
        
        # Download extra files (like webfonts) that don't need SRI hashes
        for extra in lib.get('extra_files', []):
            subdir = extra.get('subdir', '')
            if subdir:
                extra_dir = os.path.normpath(os.path.join(lib_dir, subdir))
            else:
                extra_dir = lib_dir
            os.makedirs(extra_dir, exist_ok=True)
            
            filepath = os.path.join(extra_dir, extra['filename'])
            if os.path.exists(filepath):
                if not silent:
                    print(f"Already exists: {filepath}")
            else:
                downloaded_any = True
                if not silent:
                    print(f"Downloading: {extra['url']}")
                content = download_file(extra['url'])
                with open(filepath, 'wb') as f:
                    f.write(content)
                if not silent:
                    print(f"Saved to: {filepath}")
    
    if not silent:
        print("\n" + "="*60)
        print("IMPORT TEMPLATE UPDATES:")
        print("="*60 + "\n")
        
        for lib_name, lib_data in results.items():
            print(f"<!-- {lib_name} -->")
            for f in lib_data['files']:
                print(f"<!-- Original URL: {f['original_url']} -->")
                if f['filename'].endswith('.css'):
                    print(f'<link rel="stylesheet" href="{{{{ url_for(\'static\', filename=\'libs/vendor/{lib_name}/{f["filename"]}\') }}}}" integrity="{f["integrity"]}" crossorigin="anonymous">')
                else:
                    print(f'<script src="{{{{ url_for(\'static\', filename=\'libs/vendor/{lib_name}/{f["filename"]}\') }}}}" integrity="{f["integrity"]}" crossorigin="anonymous"></script>')
            print()
    
    # Generate metadata JSON file for third-party libraries page
    generate_libraries_metadata()
    
    return downloaded_any


def generate_libraries_metadata():
    """Generate a JSON file with library metadata for the third-party libraries page."""
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'libraries': []
    }
    
    # Combine downloaded and static libraries
    all_libraries = LIBRARIES + STATIC_LIBRARIES
    
    for lib in all_libraries:
        lib_info = {
            'name': lib['name'],
            'display_name': lib.get('display_name', lib['name']),
            'version': lib.get('version', 'unknown'),
            'license': lib.get('license', 'unknown'),
            'homepage': lib.get('homepage', ''),
            'github': lib.get('github', ''),
            'license_url': lib.get('license_url', ''),
        }
        
        # Add note if present
        if lib.get('note'):
            lib_info['note'] = lib['note']
        
        # Build GitHub URLs for license/notice based on version tag
        if lib_info['github']:
            github_repo = lib_info['github']
            version = lib_info['version']
            # Construct the GitHub repo URL
            lib_info['github_url'] = f"https://github.com/{github_repo}"
            # If we have a specific version, link to that tag
            if version and version not in ('latest', 'unknown'):
                lib_info['github_tag_url'] = f"https://github.com/{github_repo}/tree/v{version}"
            else:
                lib_info['github_tag_url'] = f"https://github.com/{github_repo}"
        
        metadata['libraries'].append(lib_info)
    
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def get_libraries():
    """Get the list of all libraries with metadata. Used by the app."""
    return LIBRARIES + STATIC_LIBRARIES


def main():
    """CLI entry point."""
    download_vendor_libs(silent=False)


if __name__ == '__main__':
    main()
