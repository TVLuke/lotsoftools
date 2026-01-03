# GeoLite2 Database Setup

The IP Lookup tool requires MaxMind GeoLite2 databases to function.

## Download Instructions

1. **Sign up for a free MaxMind account:**
   - Go to https://www.maxmind.com/en/geolite2/signup
   - Create a free account

2. **Download the databases:**
   - Log in to your MaxMind account
   - Go to "Download Files" section
   - Download these two databases:
     - **GeoLite2 City** (GeoLite2-City.mmdb) - ~60MB
     - **GeoLite2 ASN** (GeoLite2-ASN.mmdb) - ~5MB

3. **Place the files:**
   - Create a directory: `mkdir -p geoip_data`
   - Extract and copy the `.mmdb` files to the `geoip_data` directory:
     ```
     geoip_data/
     ├── GeoLite2-City.mmdb
     └── GeoLite2-ASN.mmdb
     ```

## Alternative: Direct Download (requires license key)

If you have a MaxMind license key, you can download directly:

```bash
# Set your license key
export MAXMIND_LICENSE_KEY="your_license_key_here"

# Create directory
mkdir -p geoip_data

# Download City database
curl "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${MAXMIND_LICENSE_KEY}&suffix=tar.gz" -o GeoLite2-City.tar.gz
tar -xzf GeoLite2-City.tar.gz
mv GeoLite2-City_*/GeoLite2-City.mmdb geoip_data/
rm -rf GeoLite2-City* 

# Download ASN database
curl "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN&license_key=${MAXMIND_LICENSE_KEY}&suffix=tar.gz" -o GeoLite2-ASN.tar.gz
tar -xzf GeoLite2-ASN.tar.gz
mv GeoLite2-ASN_*/GeoLite2-ASN.mmdb geoip_data/
rm -rf GeoLite2-ASN*
```

## Updating Databases

MaxMind updates the GeoLite2 databases regularly (typically weekly). To keep your data current:

1. Re-download the databases from your MaxMind account
2. Replace the old `.mmdb` files in the `geoip_data` directory
3. Restart the Flask application

## License

This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.

The GeoLite2 databases are distributed under the Creative Commons Attribution-ShareAlike 4.0 International License.
