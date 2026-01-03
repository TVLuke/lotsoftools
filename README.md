# Usefull

A collection of privacy-friendly utility tools. All processing happens client-side or on your own server - no data is sent to third parties.

## Features

- **Text Tools**: Letter counter, JSON/XML/YAML formatter, CSV table viewer, diff tool
- **Generators**: QR codes, UUIDs, random strings, barcodes, Lorem ipsum
- **Converters**: Base converter, unit converter, coordinate converter, Base64, subtitle formats
- **Color Tools**: Color picker, color palettes, colorblind simulator
- **Date/Time**: Calendar, date calculator, holiday calendar, clock
- **Network**: IP lookup, DNS lookup, speed test
- **Media**: Image cropper, favicon generator, YouTube downloader
- **Other**: Hash generator, IBAN validator, ASCII table, emoji search, teleprompter

## Quick Start with Docker

### Using Docker Compose (recommended)

```bash
# Clone the repository
git clone git@github.com:TVLuke/lotsoftools.git
cd lotsoftools

# Set a secret key (optional but recommended for production)
export SECRET_KEY="your-secret-key-here"

# Build and run
docker-compose up -d
```

The app will be available at `http://localhost:5000`

### Using Portainer

1. In Portainer, go to **Stacks** → **Add stack**
2. Choose **Repository** and enter the Git repository URL
3. Set the compose file path to `docker-compose.yml`
4. Add environment variables:
   - `SECRET_KEY`: A secure random string for session encryption
5. Deploy the stack

### Manual Docker Build

```bash
docker build -t usefull .
docker run -d -p 5000:5000 -v ./data:/app/data usefull
```

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download vendor libraries
python scripts/download_vendor_libs.py

# Run the app
flask run
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Secret key for session encryption | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///data/usefull.db` |
| `FLASK_ENV` | Flask environment | `production` |

### Optional: GeoIP Database

For the IP Lookup tool to work, you need MaxMind GeoLite2 databases. See [GEOIP_SETUP.md](GEOIP_SETUP.md) for instructions.

### Optional: Support Links

To add custom support/donation links, create `app/config/support_config.json`:

```json
{
  "links": [
    {
      "name": "Ko-fi",
      "url": "https://ko-fi.com/yourname",
      "icon": "fa-solid fa-mug-hot"
    }
  ]
}
```

## Project Structure

```
usefull/
├── app/
│   ├── routes/tools/      # Tool routes and JSON configs
│   ├── templates/         # Jinja2 templates
│   ├── static/           # CSS, JS, images
│   └── services/         # Backend services
├── scripts/
│   └── download_vendor_libs.py  # Downloads JS/CSS dependencies
├── data/                 # SQLite database (gitignored)
├── geoip_data/          # GeoIP databases (gitignored)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Privacy

- All text/data processing happens in your browser or on your server
- No analytics or tracking
- No external API calls except where explicitly required (e.g., holiday data)
- All JavaScript/CSS libraries are self-hosted

## License

MIT
