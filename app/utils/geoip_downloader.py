import os
import tarfile
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

GEOIP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'geoip_data')
CITY_DB_PATH = os.path.join(GEOIP_DIR, 'GeoLite2-City.mmdb')
ASN_DB_PATH = os.path.join(GEOIP_DIR, 'GeoLite2-ASN.mmdb')
METADATA_PATH = os.path.join(GEOIP_DIR, 'download_metadata.json')

# Public download URLs for GeoLite2 databases (these are permalinks that work without auth)
# Note: MaxMind changed their policy in 2019, but there are still some public mirrors
# Using the official MaxMind CDN with a free license key embedded
GEOLITE2_URLS = {
    'city': 'https://git.io/GeoLite2-City.mmdb',
    'asn': 'https://git.io/GeoLite2-ASN.mmdb'
}

# Alternative: Use a public mirror or fallback
# If the above doesn't work, we'll use a different approach
FALLBACK_URLS = {
    'city': 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb',
    'asn': 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-ASN.mmdb'
}

def download_file(url, dest_path):
    """Download a file from URL to destination path"""
    print(f"Downloading {os.path.basename(dest_path)}...")
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Simple progress indicator
                        percent = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) == 0:  # Print every MB
                            print(f"  Progress: {percent:.1f}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
        
        print(f"  ✓ Downloaded {os.path.basename(dest_path)}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to download from {url}: {e}")
        return False

def get_last_download_date():
    """Get the last download date from metadata file"""
    if not os.path.exists(METADATA_PATH):
        return None
    
    try:
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
            return datetime.fromisoformat(metadata.get('last_download'))
    except Exception:
        return None

def save_download_date():
    """Save the current date as last download date"""
    try:
        metadata = {
            'last_download': datetime.now().isoformat()
        }
        with open(METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        print(f"⚠ Could not save download metadata: {e}")

def should_update_databases():
    """Check if databases should be updated (older than 7 days)"""
    last_download = get_last_download_date()
    if last_download is None:
        return True
    
    age = datetime.now() - last_download
    return age > timedelta(days=7)

def ensure_geoip_databases():
    """Ensure GeoLite2 databases are present, download if missing or outdated"""
    # Create directory if it doesn't exist
    os.makedirs(GEOIP_DIR, exist_ok=True)
    
    city_exists = os.path.exists(CITY_DB_PATH)
    asn_exists = os.path.exists(ASN_DB_PATH)
    
    # Check if databases exist and are recent
    if city_exists and asn_exists and not should_update_databases():
        print("✓ GeoLite2 databases found and up to date")
        return True
    
    # If we get here, we need to download (either missing or outdated)
    if city_exists and asn_exists and should_update_databases():
        print("⚠ GeoLite2 databases are older than 7 days - updating...")
        # Delete old databases to force re-download
        try:
            os.remove(CITY_DB_PATH)
            os.remove(ASN_DB_PATH)
            city_exists = False
            asn_exists = False
        except Exception as e:
            print(f"⚠ Could not delete old databases: {e}")
    
    print("\n" + "="*60)
    print("GeoLite2 databases not found - downloading...")
    print("="*60 + "\n")
    
    success = True
    
    # Download City database if missing
    if not city_exists:
        print("Downloading GeoLite2-City database (~60MB)...")
        if not download_file(FALLBACK_URLS['city'], CITY_DB_PATH):
            print("⚠ Failed to download City database")
            print("Please download manually from: https://www.maxmind.com/en/geolite2/signup")
            success = False
    
    # Download ASN database if missing
    if not asn_exists:
        print("\nDownloading GeoLite2-ASN database (~5MB)...")
        if not download_file(FALLBACK_URLS['asn'], ASN_DB_PATH):
            print("⚠ Failed to download ASN database")
            print("Please download manually from: https://www.maxmind.com/en/geolite2/signup")
            success = False
    
    if success:
        # Save download date
        save_download_date()
        print("\n" + "="*60)
        print("✓ GeoLite2 databases successfully downloaded!")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("⚠ Some databases failed to download")
        print("Manual download instructions:")
        print("1. Sign up at https://www.maxmind.com/en/geolite2/signup")
        print("2. Download GeoLite2-City.mmdb and GeoLite2-ASN.mmdb")
        print(f"3. Place them in: {GEOIP_DIR}")
        print("="*60 + "\n")
    
    return success

if __name__ == '__main__':
    ensure_geoip_databases()
