from flask import Blueprint, Response, jsonify, render_template, request
import json
import os
import time
from app.services.link_service import increment_click_count
from app.utils import require_tool_active

speed_test_bp = Blueprint('speed_test', __name__, url_prefix='/tools')

DOWNLOAD_BYTES = 10 * 1024 * 1024
UPLOAD_BYTES = 5 * 1024 * 1024
CHUNK_SIZE = 64 * 1024


def _clamp_int(value, default, min_value, max_value):
    try:
        n = int(value)
    except Exception:
        return default
    return max(min_value, min(max_value, n))


@speed_test_bp.route('/speed-test')
@require_tool_active('speed_test')
def index():
    increment_click_count(request.path)

    json_path = os.path.join(os.path.dirname(__file__), 'speed_test_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)

    return render_template('tools/speed_test.html', tool_data=tool_data)


@speed_test_bp.route('/speed-test/ping')
@require_tool_active('speed_test')
def ping():
    return jsonify({'ok': True, 'ts': time.time()})


@speed_test_bp.route('/speed-test/download')
@require_tool_active('speed_test')
def download():
    total_bytes = DOWNLOAD_BYTES
    chunk_size = CHUNK_SIZE

    pattern = (b'0123456789abcdef' * 4096)  # 64 KiB

    def generate():
        remaining = total_bytes
        while remaining > 0:
            n = min(chunk_size, remaining)
            if n <= len(pattern):
                yield pattern[:n]
            else:
                # Fallback (shouldn't happen with current clamps)
                yield b'0' * n
            remaining -= n

    headers = {
        'Content-Type': 'application/octet-stream',
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
        'Pragma': 'no-cache',
        'X-Content-Type-Options': 'nosniff',
        'Content-Length': str(total_bytes),
    }

    return Response(generate(), headers=headers)


@speed_test_bp.route('/speed-test/upload', methods=['POST'])
@require_tool_active('speed_test')
def upload():
    max_bytes = UPLOAD_BYTES
    chunk_size = CHUNK_SIZE

    start = time.perf_counter()
    read_bytes = 0

    while read_bytes < max_bytes:
        chunk = request.stream.read(min(chunk_size, max_bytes - read_bytes))
        if not chunk:
            break
        read_bytes += len(chunk)

    elapsed = time.perf_counter() - start

    return jsonify({
        'ok': True,
        'bytes_received': read_bytes,
        'seconds': elapsed,
    })
