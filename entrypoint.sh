#!/bin/bash

# Install ffmpeg if not present (persists until container is recreated)
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing ffmpeg..."
    apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
    echo "✓ ffmpeg installed"
else
    echo "✓ ffmpeg already installed"
fi

# Start gunicorn
echo "Starting Lots of Tools v1.0.18"
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 1500 --preload wsgi:application
