FROM python:3.11-slim

# Version label - update this when making changes
LABEL version="1.0.18"
LABEL description="Usefull Tools Collection"

WORKDIR /app

# Install build dependencies only (ffmpeg installed at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Download vendor libraries
RUN python scripts/download_vendor_libs.py

# Create necessary directories
RUN mkdir -p data geoip_data instance

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Make entrypoint executable and use it
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
