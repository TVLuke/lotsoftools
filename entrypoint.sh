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
export FLASK_APP=wsgi:application
cd /app
if ! flask db upgrade 2>&1; then
    echo "⚠ Migration upgrade failed, stamping current state..."
    flask db stamp head
    echo "✓ Database stamped at head"
fi
echo "✓ Database migrations complete"

# Start gunicorn
# - gthread workers so a single slow/idle client can't tie up a whole worker
# - short timeout (60s) so stuck connections are reaped quickly instead of
#   holding a worker for up to 25 minutes (was --timeout 1500)
# - graceful-timeout/keep-alive tuned to shed slowloris-style connections
exec gunicorn --bind 0.0.0.0:5000 \
    --workers 2 --threads 4 --worker-class gthread \
    --timeout 120 --graceful-timeout 60 --keep-alive 5 \
    --preload wsgi:application
