# Lots of tools

I got fed up.

Fed up with all these single-purpose websites full of tracking cookies, commercials, pop-ups, and shady buttons that serve you malware. You know the ones — they're always the first results in Google, not because they're good, but because they've SEO'd and paid their way to the top. They're infested with ads, harvest your data, and make you click through five screens just to get a UUID or generate a QR code.

Sure, there are some very good ones out there. But the overall state of these "simple online tools" is horrible.

So I decided: whenever I was about to type something like "qr-code generator" or "uuid generator" or "map calculate distance" into a search engine, I would instead just build my own.

This is that growing collection of tools. Privacy-friendly, no tracking, no ads — wherever possible, processing happens client-side. If data is send to the service this is indicated by a color in the icon and stated in the description. If data is send anywhere else this is clearly stated as well. 

If these tools are of any help to you, great. You can run your own instance if you want. I am running an instance at [lotsof.tools](https://lotsof.tools).

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

### Optional: Privacy Policy Content

To add your own privacy policy text, create HTML files in `app/config/`:

- `privacy_content.en.html` - English content
- `privacy_content.de.html` - German content

See `privacy_content.example.en.html` and `privacy_content.example.de.html` for examples. The content supports full HTML formatting with headings, paragraphs, lists, and links.

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

## Note on Use of LLMs

This code was created using, among other tools, LLM tools like ChatGPT.
