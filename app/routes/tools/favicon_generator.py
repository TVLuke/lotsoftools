from flask import Blueprint, render_template, request, send_file, jsonify
import json
import os
from PIL import Image
from app.services.link_service import increment_click_count
import io
import zipfile
from datetime import datetime, timedelta
import threading
import time
import uuid
from werkzeug.utils import secure_filename

favicon_generator_bp = Blueprint('favicon_generator', __name__, url_prefix='/tools')

# Directory for temporary files
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp_favicons')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB in bytes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Remove files older than 5 minutes"""
    while True:
        try:
            now = datetime.now()
            for item in os.listdir(UPLOAD_FOLDER):
                item_path = os.path.join(UPLOAD_FOLDER, item)
                if os.path.isfile(item_path) or os.path.isdir(item_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                    if now - file_time > timedelta(minutes=5):
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            import shutil
                            shutil.rmtree(item_path)
        except Exception as e:
            print(f"Cleanup error: {e}")
        time.sleep(60)  # Check every minute

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

def generate_favicons_from_image(img, output_dir):
    """Generate all favicon files from PIL Image object"""
    # Image is already loaded and converted to RGBA by caller
    
    # Generate different sizes
    sizes = {
        'favicon-96x96.png': (96, 96),
        'apple-touch-icon.png': (180, 180),
        'web-app-manifest-192x192.png': (192, 192),
        'web-app-manifest-512x512.png': (512, 512),
    }
    
    for filename, size in sizes.items():
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(os.path.join(output_dir, filename), 'PNG')
    
    # Generate favicon.ico (16x16, 32x32, 48x48)
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    ico_images = [img.resize(size, Image.Resampling.LANCZOS) for size in ico_sizes]
    ico_images[0].save(
        os.path.join(output_dir, 'favicon.ico'),
        format='ICO',
        sizes=ico_sizes
    )
    
    # Generate SVG (simplified - just save as PNG for now, proper SVG would need conversion)
    # For a proper implementation, you'd use a library like cairosvg or potrace
    svg_img = img.resize((512, 512), Image.Resampling.LANCZOS)
    svg_img.save(os.path.join(output_dir, 'favicon.svg'), 'PNG')
    
    # Generate site.webmanifest
    manifest = {
        "name": "MyWebSite",
        "short_name": "MySite",
        "icons": [
            {
                "src": "/web-app-manifest-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable"
            },
            {
                "src": "/web-app-manifest-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable"
            }
        ],
        "theme_color": "#ffffff",
        "background_color": "#ffffff",
        "display": "standalone"
    }
    
    with open(os.path.join(output_dir, 'site.webmanifest'), 'w') as f:
        json.dump(manifest, f, indent=2)

@favicon_generator_bp.route('/favicon-generator')
def index():
    increment_click_count(request.path)
    
    # Load tool data from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'favicon_generator_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/favicon_generator.html', tool_data=tool_data)

@favicon_generator_bp.route('/favicon-generator/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PNG or JPEG'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Maximum size is 2MB'}), 400
    
    try:
        # Create unique directory for this generation
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(UPLOAD_FOLDER, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        # Load image directly into memory from uploaded file
        img = Image.open(file.stream)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Generate favicons from in-memory image
        generate_favicons_from_image(img, job_dir)
        
        # Create ZIP file
        zip_path = os.path.join(UPLOAD_FOLDER, f'{job_id}.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir(job_dir):
                file_path = os.path.join(job_dir, filename)
                zipf.write(file_path, filename)
        
        # Delete job directory immediately after ZIP creation
        import shutil
        shutil.rmtree(job_dir)
        
        return jsonify({
            'success': True,
            'download_id': job_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@favicon_generator_bp.route('/favicon-generator/download/<download_id>')
def download(download_id):
    zip_path = os.path.join(UPLOAD_FOLDER, f'{download_id}.zip')
    
    if not os.path.exists(zip_path):
        return "File not found or expired", 404
    
    return send_file(
        zip_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name='favicons.zip'
    )
