from flask import Blueprint, render_template, request, send_file, jsonify
import json
import os
import tempfile
import zipfile
from datetime import datetime
import threading
import time
import yt_dlp
from werkzeug.utils import secure_filename
from app.services.link_service import increment_click_count
from app.utils import require_tool_active

youtube_dl_bp = Blueprint('youtube_dl', __name__, url_prefix='/tools')

# Temporary directory for downloads
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'youtube_dl')
CLEANUP_DELAY = 60  # 1 minute

_TEMP_DIR_CLEANED = False

def ensure_temp_dir():
    """Ensure temporary directory exists"""
    os.makedirs(TEMP_DIR, exist_ok=True)


def _cleanup_temp_dir_once():
    global _TEMP_DIR_CLEANED
    if _TEMP_DIR_CLEANED:
        return
    _TEMP_DIR_CLEANED = True

    try:
        ensure_temp_dir()
        for name in os.listdir(TEMP_DIR):
            path = os.path.join(TEMP_DIR, name)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
            except Exception:
                pass
    except Exception:
        pass


_cleanup_temp_dir_once()

def cleanup_file(filepath, delay):
    """Delete file after delay"""
    def delete():
        time.sleep(delay)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Deleted: {filepath}")
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")
    
    thread = threading.Thread(target=delete, daemon=True)
    thread.start()

@youtube_dl_bp.route('/youtube-dl')
@require_tool_active('youtube_dl')
def index():
    increment_click_count(request.path)
    
    json_path = os.path.join(os.path.dirname(__file__), 'youtube_dl_tool.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        tool_data = json.load(f)
    
    return render_template('tools/youtube_dl.html', tool_data=tool_data)

@youtube_dl_bp.route('/youtube-dl/download', methods=['POST'])
@require_tool_active('youtube_dl')
def download():
    """Download YouTube video or audio"""
    ensure_temp_dir()
    
    data = request.get_json()
    url = data.get('url', '').strip()
    format_type = data.get('format', 'video')  # 'video' or 'audio'
    metadata = data.get('metadata') if isinstance(data, dict) else None
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Validate URL
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')

    try:
        print(f"youtube-dl: starting download url={url} format={format_type} ts={timestamp}")

        def progress_hook(d):
            status = d.get('status')
            if status == 'downloading':
                downloaded = d.get('downloaded_bytes')
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                if downloaded is not None and total:
                    percent = (downloaded / total) * 100
                    print(f"[download] {percent:.1f}% ({downloaded}/{total})")
                else:
                    print("[download] downloading...")
            elif status == 'finished':
                print("[download] finished, now processing")

        output_template = os.path.join(TEMP_DIR, f'{timestamp}_%(title)s.%(ext)s')

        if format_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'progress_hooks': [progress_hook],
            }
        else:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'progress_hooks': [progress_hook],
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'download')

        downloaded_file = None
        candidates = []
        try:
            for name in os.listdir(TEMP_DIR):
                if not name.startswith(timestamp):
                    continue
                if name.endswith('.part') or name.endswith('.ytdl'):
                    continue
                path = os.path.join(TEMP_DIR, name)
                if os.path.isfile(path):
                    candidates.append(path)
        except Exception:
            candidates = []

        if format_type == 'audio':
            mp3_candidates = [p for p in candidates if p.lower().endswith('.mp3')]
            if mp3_candidates:
                downloaded_file = max(mp3_candidates, key=lambda p: os.path.getmtime(p))
            elif candidates:
                downloaded_file = max(candidates, key=lambda p: os.path.getmtime(p))
        else:
            mp4_candidates = [p for p in candidates if p.lower().endswith('.mp4')]
            if mp4_candidates:
                downloaded_file = max(mp4_candidates, key=lambda p: os.path.getmtime(p))
            elif candidates:
                downloaded_file = max(candidates, key=lambda p: os.path.getmtime(p))

        if not downloaded_file or not os.path.exists(downloaded_file):
            return jsonify({'error': 'Download failed - file not found'}), 500

        if format_type == 'audio' and metadata:
            if not downloaded_file.lower().endswith('.mp3'):
                print(f"youtube-dl: metadata provided but output is not mp3, skipping tags file={downloaded_file}")
            else:
                try:
                    from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TALB, TRCK, TDRC, TCON, COMM

                    def _val(key):
                        v = metadata.get(key) if isinstance(metadata, dict) else None
                        if v is None:
                            return None
                        v = str(v).strip()
                        return v if v else None

                    title = _val('title')
                    artist = _val('artist')
                    album = _val('album')
                    track = _val('track')
                    year = _val('year')
                    genre = _val('genre')
                    comment = _val('comment')

                    if not any([title, artist, album, track, year, genre, comment]):
                        print("youtube-dl: metadata provided but all fields empty, skipping tags")
                    else:
                        print(
                            "youtube-dl: applying id3 tags "
                            f"title={bool(title)} artist={bool(artist)} album={bool(album)} "
                            f"track={bool(track)} year={bool(year)} genre={bool(genre)} comment={bool(comment)}"
                        )

                    try:
                        tags = ID3(downloaded_file)
                    except ID3NoHeaderError:
                        tags = ID3()

                    if title:
                        tags.add(TIT2(encoding=3, text=title))
                    if artist:
                        tags.add(TPE1(encoding=3, text=artist))
                    if album:
                        tags.add(TALB(encoding=3, text=album))
                    if track:
                        tags.add(TRCK(encoding=3, text=track))
                    if year:
                        tags.add(TDRC(encoding=3, text=year))
                    if genre:
                        tags.add(TCON(encoding=3, text=genre))
                    if comment:
                        tags.add(COMM(encoding=3, lang='eng', desc='', text=comment))

                    tags.save(downloaded_file, v2_version=3)
                    print(f"youtube-dl: wrote ID3 tags file={downloaded_file}")
                except Exception as e:
                    print(f"youtube-dl: failed to write ID3 tags: {e}")

        safe_title = secure_filename(video_title)
        zip_filename = f'{timestamp}_{safe_title}.zip'
        zip_path = os.path.join(TEMP_DIR, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(downloaded_file, os.path.basename(downloaded_file))

        os.remove(downloaded_file)

        cleanup_file(zip_path, CLEANUP_DELAY)

        return jsonify({
            'success': True,
            'download_id': os.path.basename(zip_path),
            'title': video_title,
        })
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@youtube_dl_bp.route('/youtube-dl/get/<filename>')
@require_tool_active('youtube_dl')
def get_file(filename):
    """Serve the downloaded file"""
    file_path = os.path.join(TEMP_DIR, filename)
    
    if not os.path.exists(file_path):
        return "File not found or expired", 404
    
    return send_file(
        file_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )
