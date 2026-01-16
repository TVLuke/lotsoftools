#!/bin/bash

# Check if youtube_dl is enabled in tool_config.json
YOUTUBE_DL_ACTIVE=$(python3 -c "import json; print(json.load(open('/app/app/config/tool_config.json')).get('youtube_dl', {}).get('active', False))" 2>/dev/null)

# Install ffmpeg only if youtube_dl is active
if [ "$YOUTUBE_DL_ACTIVE" = "True" ]; then
    if ! command -v ffmpeg &> /dev/null; then
        echo "Installing ffmpeg (required for youtube-dl)..."
        apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
        echo "✓ ffmpeg installed"
    else
        echo "✓ ffmpeg already installed"
    fi
else
    echo "○ ffmpeg skipped (youtube-dl not active)"
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade
echo "✓ Database migrations complete"

# Start gunicorn
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 1500 --preload wsgi:application
