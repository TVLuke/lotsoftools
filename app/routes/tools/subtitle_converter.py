from flask import Blueprint, render_template, request, send_file, jsonify
import pysubs2
import json
import os
import tempfile
import zipfile
from datetime import datetime
import threading
import time
from werkzeug.utils import secure_filename
from app.services.link_service import increment_click_count

subtitle_converter_bp = Blueprint('subtitle_converter', __name__, url_prefix='/tools')

# Temporary directory for subtitle files
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'subtitle_converter')
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
CLEANUP_DELAY = 300  # 5 minutes

# Supported formats - just file extensions for output
FORMATS = {
    'srt': 'srt',
    'ass': 'ass',
    'ssa': 'ssa',
    'vtt': 'vtt',
    'ttml': 'ttml',
    'sami': 'sami',
    'tmp': 'tmp',
    'mpl2': 'mpl2',
    'microdvd': 'microdvd'
}

def ensure_temp_dir():
    """Ensure temporary directory exists"""
    os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_file(filepath, delay=CLEANUP_DELAY):
    """Delete file after delay"""
    def delete_after_delay():
        time.sleep(delay)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Cleaned up: {filepath}")
        except Exception as e:
            print(f"Error cleaning up {filepath}: {e}")
    
    thread = threading.Thread(target=delete_after_delay, daemon=True)
    thread.start()

def get_format_from_filename(filename):
    """Extract format from filename extension"""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else None
    return FORMATS.get(ext)

@subtitle_converter_bp.route('/subtitle-converter')
def index():
    """Subtitle converter page"""
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'subtitle_converter_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/subtitle_converter.html', tool_data=tool_data, formats=FORMATS)

@subtitle_converter_bp.route('/subtitle-converter/convert', methods=['POST'])
def convert():
    """Convert subtitle file"""
    ensure_temp_dir()
    
    # Validate file upload
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.1f} MB'}), 400
    
    # Get target format
    target_format = request.form.get('format', '').lower()
    if target_format not in FORMATS:
        return jsonify({'error': f'Invalid target format: {target_format}'}), 400
    
    # Save uploaded file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    original_filename = secure_filename(file.filename)
    input_path = os.path.join(TEMP_DIR, f'{timestamp}_input_{original_filename}')
    
    try:
        file.save(input_path)
        
        # Load subtitle file - let pysubs2 auto-detect the format
        try:
            subs = pysubs2.load(input_path)
        except Exception as e:
            os.remove(input_path)
            return jsonify({'error': f'Failed to parse subtitle file: {str(e)}'}), 400
        
        # Convert to target format
        base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
        output_filename = f'{base_name}.{target_format}'
        output_path = os.path.join(TEMP_DIR, f'{timestamp}_output_{output_filename}')
        
        try:
            subs.save(output_path)
        except Exception as e:
            os.remove(input_path)
            return jsonify({'error': f'Failed to convert subtitle: {str(e)}'}), 400
        
        # Create zip file
        zip_filename = f'{base_name}_converted.zip'
        zip_path = os.path.join(TEMP_DIR, f'{timestamp}_output.zip')
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(output_path, output_filename)
        except Exception as e:
            os.remove(input_path)
            os.remove(output_path)
            return jsonify({'error': f'Failed to create zip file: {str(e)}'}), 400
        
        # Clean up input and output files immediately
        os.remove(input_path)
        os.remove(output_path)
        
        # Schedule zip cleanup after 5 minutes
        cleanup_file(zip_path)
        
        # Send zip file
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
        
    except Exception as e:
        # Clean up any files that were created
        for path in [input_path, output_path if 'output_path' in locals() else None, 
                     zip_path if 'zip_path' in locals() else None]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500
