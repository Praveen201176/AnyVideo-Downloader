"""
AnyVideo Downloader - Advanced Video Downloader
Developer: dr1p7.steez
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import yt_dlp
import os
import json
import threading
import time
from datetime import datetime
import re
from config import Config
from utils import print_banner
from security import (
    SecurityValidator, 
    RequestValidator, 
    AntiAbuse, 
    secure_headers
)

app = Flask(__name__)

# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Security headers (only in production)
if not Config.DEBUG:
    csp = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdnjs.cloudflare.com"],
        'style-src': ["'self'", "'unsafe-inline'", "cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "cdnjs.cloudflare.com"]
    }
    Talisman(app, content_security_policy=csp, force_https=False)

# Initialize configuration
Config.init_app()
DOWNLOAD_FOLDER = Config.DOWNLOAD_FOLDER

# Global variables to track downloads
download_progress = {}
download_history = []

class DownloadLogger:
    def __init__(self, download_id):
        self.download_id = download_id
        
    def debug(self, msg):
        pass
    
    def warning(self, msg):
        pass
    
    def error(self, msg):
        download_progress[self.download_id]['status'] = 'error'
        download_progress[self.download_id]['error'] = msg

def progress_hook(d, download_id):
    """Hook to track download progress"""
    if d['status'] == 'downloading':
        download_progress[download_id]['status'] = 'downloading'
        # Extract just the filename, not the full path
        full_path = d.get('filename', 'Unknown')
        download_progress[download_id]['filename'] = os.path.basename(full_path)
        
        # Calculate progress
        if 'total_bytes' in d:
            total = d['total_bytes']
            downloaded = d.get('downloaded_bytes', 0)
            percent = (downloaded / total) * 100
            download_progress[download_id]['progress'] = percent
            download_progress[download_id]['downloaded'] = downloaded
            download_progress[download_id]['total'] = total
            download_progress[download_id]['speed'] = d.get('speed', 0)
            download_progress[download_id]['eta'] = d.get('eta', 0)
        elif 'total_bytes_estimate' in d:
            total = d['total_bytes_estimate']
            downloaded = d.get('downloaded_bytes', 0)
            percent = (downloaded / total) * 100
            download_progress[download_id]['progress'] = percent
            download_progress[download_id]['downloaded'] = downloaded
            download_progress[download_id]['total'] = total
            download_progress[download_id]['speed'] = d.get('speed', 0)
            download_progress[download_id]['eta'] = d.get('eta', 0)
    
    elif d['status'] == 'finished':
        download_progress[download_id]['status'] = 'processing'
        download_progress[download_id]['progress'] = 100
        # Extract just the filename, not the full path
        full_path = d.get('filename', 'Unknown')
        download_progress[download_id]['filename'] = os.path.basename(full_path)
    
    elif d['status'] == 'error':
        download_progress[download_id]['status'] = 'error'
        download_progress[download_id]['error'] = str(d.get('error', 'Unknown error'))

def download_video(url, download_id, quality='best', format_type='video'):
    """Download video in a separate thread with advanced bypass capabilities"""
    try:
        download_progress[download_id]['status'] = 'starting'
        
        # Configure yt-dlp options with advanced bypass features
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'logger': DownloadLogger(download_id),
            
            # Advanced bypass options
            'nocheckcertificate': True,
            'no_warnings': False,
            'ignoreerrors': False,
            
            # Geo-restriction bypass
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            
            # User agent and headers (mimic real browser)
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            },
            
            # Retry settings
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'extractor_retries': 5,
            
            # Age restriction bypass
            'age_limit': None,
            
            # Network optimization
            'socket_timeout': 30,
            'source_address': None,  # Bind to default interface
            
            # Extractor arguments for better compatibility
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web', 'ios'],
                    'player_skip': ['configs'],
                    'skip': ['hls'],
                },
                'generic': {
                    'forced': False,
                }
            },
            
            # Additional options
            'prefer_insecure': False,
            'no_check_certificate': True,
            'call_home': False,
        }
        
        # Quality and format settings with multiple fallbacks
        if format_type == 'video':
            if quality == 'best':
                # Try multiple format combinations for best compatibility
                ydl_opts['format'] = (
                    'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                    'bestvideo+bestaudio/'
                    'best[ext=mp4]/'
                    'best'
                )
                ydl_opts['merge_output_format'] = 'mp4'
            elif quality == '4k':
                ydl_opts['format'] = (
                    'bestvideo[height>=2160][ext=mp4]+bestaudio[ext=m4a]/'
                    'bestvideo[height>=2160]+bestaudio/'
                    'best[height>=2160]/'
                    'bestvideo+bestaudio/'
                    'best'
                )
                ydl_opts['merge_output_format'] = 'mp4'
            elif quality == '1080p':
                ydl_opts['format'] = (
                    'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/'
                    'bestvideo[height<=1080]+bestaudio/'
                    'best[height<=1080]/'
                    'best'
                )
                ydl_opts['merge_output_format'] = 'mp4'
            elif quality == '720p':
                ydl_opts['format'] = (
                    'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/'
                    'bestvideo[height<=720]+bestaudio/'
                    'best[height<=720]/'
                    'best'
                )
                ydl_opts['merge_output_format'] = 'mp4'
        elif format_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
            ydl_opts['keepvideo'] = False
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            download_progress[download_id]['title'] = info.get('title', 'Unknown')
            download_progress[download_id]['thumbnail'] = info.get('thumbnail', '')
            download_progress[download_id]['duration'] = info.get('duration', 0)
            download_progress[download_id]['uploader'] = info.get('uploader', 'Unknown')
            
            # Download the video
            ydl.download([url])
            
            # Mark as completed
            download_progress[download_id]['status'] = 'completed'
            download_progress[download_id]['progress'] = 100
            download_progress[download_id]['completed_at'] = datetime.now().isoformat()
            
            # Add to history
            download_history.append({
                'id': download_id,
                'url': url,
                'title': download_progress[download_id]['title'],
                'quality': quality,
                'format': format_type,
                'completed_at': download_progress[download_id]['completed_at'],
                'filename': download_progress[download_id].get('filename', '')
            })
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error downloading {url}: {error_msg}")
        download_progress[download_id]['status'] = 'error'
        
        # Provide helpful error messages
        if 'DRM' in error_msg or 'drm protection' in error_msg.lower():
            download_progress[download_id]['error'] = 'DRM-protected content cannot be downloaded. Use official app (Netflix, Disney+, etc.)'
        elif 'need to log in' in error_msg.lower() or 'login required' in error_msg.lower() or 'cookies' in error_msg.lower() or 'nsfw' in error_msg.lower():
            download_progress[download_id]['error'] = 'Login required. Export cookies from browser. See COOKIE_GUIDE.md'
        elif 'Unsupported URL' in error_msg or 'No video formats found' in error_msg:
            download_progress[download_id]['error'] = 'Site not supported or outdated. Update yt-dlp: pip install --upgrade yt-dlp'
        elif 'HTTP Error 404' in error_msg:
            download_progress[download_id]['error'] = 'Video not found (404). Video may be deleted or URL incorrect.'
        elif 'Unable to extract' in error_msg or 'Failed to parse' in error_msg:
            download_progress[download_id]['error'] = 'Extraction failed. Update yt-dlp: pip install --upgrade yt-dlp'
        elif 'Cloudflare' in error_msg or 'HTTP Error 403' in error_msg or 'impersonate' in error_msg:
            download_progress[download_id]['error'] = 'Cloudflare protected. Install: pip install curl-cffi, then restart'
        else:
            download_progress[download_id]['error'] = error_msg

@app.route('/')
@secure_headers()
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'suggestion': 'Please wait a moment before trying again',
        'details': 'Too many requests. Please slow down.'
    }), 429

@app.errorhandler(413)
def request_too_large(e):
    """Handle request too large errors"""
    return jsonify({
        'error': 'Request too large',
        'suggestion': 'The request payload is too large'
    }), 413

@app.errorhandler(400)
def bad_request(e):
    """Handle bad request errors"""
    return jsonify({
        'error': 'Bad request',
        'suggestion': 'Please check your request format'
    }), 400

@app.route('/api/download', methods=['POST'])
@limiter.limit("10 per minute")
@RequestValidator.check_request_size(max_size=2048)
@RequestValidator.validate_json_request(required_fields=['url'])
@secure_headers()
def start_download():
    """Start a video download with security validation"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        quality = data.get('quality', 'best')
        format_type = data.get('format', 'video')
        
        # Validate URL
        is_valid, error_msg = SecurityValidator.validate_url(url)
        if not is_valid:
            return jsonify({
                'error': 'Invalid URL',
                'suggestion': error_msg
            }), 400
        
        # Validate quality
        is_valid, quality = SecurityValidator.validate_quality(quality)
        if not is_valid:
            return jsonify({
                'error': 'Invalid quality parameter'
            }), 400
        
        # Validate format
        is_valid, format_type = SecurityValidator.validate_format(format_type)
        if not is_valid:
            return jsonify({
                'error': 'Invalid format parameter'
            }), 400
        
        # Generate unique download ID
        download_id = f"download_{int(time.time() * 1000)}"
        
        # Initialize progress tracking
        download_progress[download_id] = {
            'id': download_id,
            'url': url,
            'status': 'queued',
            'progress': 0,
            'quality': quality,
            'format': format_type,
            'started_at': datetime.now().isoformat()
        }
        
        # Start download in a separate thread
        thread = threading.Thread(target=download_video, args=(url, download_id, quality, format_type))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'Download started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<download_id>', methods=['GET'])
@limiter.limit("60 per minute")
@secure_headers()
def get_progress(download_id):
    """Get download progress with validation"""
    # Sanitize download_id
    download_id = SecurityValidator.sanitize_string(download_id, max_length=50)
    
    # Validate format (should be download_TIMESTAMP)
    if not re.match(r'^download_\d+$', download_id):
        return jsonify({'error': 'Invalid download ID'}), 400
    
    if download_id in download_progress:
        return jsonify(download_progress[download_id])
    else:
        return jsonify({'error': 'Download not found'}), 404

@app.route('/api/info', methods=['POST'])
@limiter.limit("20 per minute")
@RequestValidator.check_request_size(max_size=2048)
@RequestValidator.validate_json_request(required_fields=['url'])
@secure_headers()
def get_video_info():
    """Get video information without downloading - with security validation"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        # Validate URL
        is_valid, error_msg = SecurityValidator.validate_url(url)
        if not is_valid:
            return jsonify({
                'error': 'Invalid URL',
                'suggestion': error_msg,
                'details': 'Please provide a valid HTTP/HTTPS URL'
            }), 400
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            
            # Bypass options for info extraction
            'nocheckcertificate': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'age_limit': None,
            
            # Headers
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': url,
            },
            
            # Extractor arguments
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                },
            },
            
            # Retry settings
            'retries': 5,
            'extractor_retries': 3,
            
            # Force generic extractor as fallback
            'default_search': 'auto',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as extract_error:
            # Check for various error types
            error_str = str(extract_error)
            print(f"Primary extraction failed with error: {repr(extract_error)}")
            print(f"Error type: {type(extract_error).__name__}")
            print(f"Error message: {error_str}")
            
            # Check for DRM protection
            if 'DRM' in error_str or 'drm protection' in error_str.lower():
                return jsonify({
                    'error': 'This content is DRM-protected and cannot be downloaded.',
                    'suggestion': 'DRM bypass is illegal and not supported. Use official apps (Netflix, Disney+, etc.) to watch.',
                    'details': 'Services like Netflix, Disney+, Amazon Prime, Hulu, HBO Max use DRM encryption which is legally protected.'
                }), 500
            
            if 'need to log in' in error_str.lower() or 'login required' in error_str.lower():
                return jsonify({
                    'error': 'This content requires login/authentication.',
                    'suggestion': 'This is private content. See COOKIE_GUIDE.md for cookie export instructions.',
                    'details': error_str
                }), 500
            
            # If extractor fails, try with force_generic_extractor
            print(f"Trying generic extractor as fallback...")
            try:
                ydl_opts['force_generic_extractor'] = True
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                print("Generic extractor succeeded!")
            except Exception as generic_error:
                # Generic extractor also failed, re-raise original error
                print(f"Generic extractor also failed with error: {repr(generic_error)}")
                print(f"Error message: {str(generic_error)}")
                raise extract_error
            
        # Extract available formats
        formats = []
        if 'formats' in info:
            seen_heights = set()
            for f in info['formats']:
                height = f.get('height')
                if height and height not in seen_heights:
                    formats.append({
                        'quality': f"{height}p",
                        'height': height,
                        'ext': f.get('ext', 'mp4')
                    })
                    seen_heights.add(height)
            
            # Sort by height descending
            formats.sort(key=lambda x: x['height'], reverse=True)
        
        return jsonify({
            'success': True,
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'thumbnail': info.get('thumbnail', ''),
            'uploader': info.get('uploader', 'Unknown'),
            'description': info.get('description', '')[:200],
            'view_count': info.get('view_count', 0),
            'formats': formats[:10]  # Limit to top 10 formats
        })
            
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if 'DRM' in error_msg or 'drm protection' in error_msg.lower():
            return jsonify({
                'error': 'This content is DRM-protected and cannot be downloaded.',
                'suggestion': 'DRM bypass is illegal and not supported. Use official apps to watch.',
                'details': 'Services like Netflix, Disney+, Amazon Prime, Hulu use DRM encryption which is legally protected and cannot be bypassed.'
            }), 500
        elif 'need to log in' in error_msg.lower() or 'login required' in error_msg.lower() or 'cookies' in error_msg.lower() or 'nsfw' in error_msg.lower():
            return jsonify({
                'error': 'This content requires login/authentication.',
                'suggestion': 'Export cookies from your browser. See COOKIE_GUIDE.md for instructions.',
                'details': 'Private, protected, or NSFW content requires you to be logged in.'
            }), 500
        elif 'Unsupported URL' in error_msg:
            return jsonify({
                'error': 'This site is not supported or the URL format is incorrect.',
                'suggestion': 'Try updating yt-dlp: Run update_ytdlp.bat or: pip install --upgrade yt-dlp',
                'details': error_msg
            }), 500
        elif 'No video formats found' in error_msg:
            return jsonify({
                'error': 'No video formats found. The site may have changed its format.',
                'suggestion': 'Update yt-dlp: Run update_ytdlp.bat or: pip install --upgrade yt-dlp',
                'details': error_msg
            }), 500
        elif 'HTTP Error 404' in error_msg:
            return jsonify({
                'error': 'Video not found (404). The video may have been deleted or the URL is incorrect.',
                'suggestion': 'Check the URL and try again.',
                'details': error_msg
            }), 500
        elif 'Unable to extract' in error_msg or 'Failed to parse' in error_msg:
            return jsonify({
                'error': 'Failed to extract video information. The site format may have changed.',
                'suggestion': 'Update yt-dlp: Run update_ytdlp.bat or: pip install --upgrade yt-dlp',
                'details': error_msg
            }), 500
        elif 'Cloudflare' in error_msg or 'HTTP Error 403' in error_msg or 'impersonate' in error_msg:
            return jsonify({
                'error': 'Site is protected by Cloudflare anti-bot.',
                'suggestion': 'Install bypass: pip install curl-cffi, then restart. See CLOUDFLARE_BYPASS.md',
                'details': error_msg
            }), 500
        else:
            return jsonify({
                'error': error_msg,
                'suggestion': 'Try updating yt-dlp: Run update_ytdlp.bat or: pip install --upgrade yt-dlp'
            }), 500

@app.route('/api/history', methods=['GET'])
@limiter.limit("30 per minute")
@secure_headers()
def get_history():
    """Get download history"""
    # Limit history to last 50 items for security
    return jsonify(download_history[-50:])

@app.route('/api/downloads', methods=['GET'])
@limiter.limit("20 per minute")
@secure_headers()
def list_downloads():
    """List all files in download folder with security"""
    try:
        files = []
        for filename in os.listdir(DOWNLOAD_FOLDER):
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/supported-sites', methods=['GET'])
@limiter.limit("10 per minute")
@secure_headers()
def supported_sites():
    """Get list of supported sites"""
    # Return a curated list of popular supported sites
    sites = [
        'YouTube', 'Vimeo', 'TikTok', 'Twitter/X', 'Instagram', 'Facebook',
        'Dailymotion', 'Twitch', 'Reddit', 'SoundCloud', 'Bandcamp',
        'VK', 'Rumble', 'Odysoe', 'Bilibili', 'Niconico', 'Archive.org',
        'And 1000+ more sites...'
    ]
    return jsonify(sites)

@app.route('/api/file/<path:filename>', methods=['GET'])
@limiter.limit("20 per minute")
@secure_headers()
def download_file(filename):
    """Serve downloaded file to user's browser"""
    try:
        # Security: prevent directory traversal
        filename = os.path.basename(filename)
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Send file to browser with download prompt
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"⚠️ Error serving file {filename}: {e}")
        return jsonify({'error': str(e)}), 500

def cleanup_old_downloads():
    """
    Delete downloads older than 30 seconds to prevent storage bloat
    Perfect for free hosting services - files auto-delete after download
    """
    try:
        current_time = time.time()
        cleanup_count = 0
        
        for filename in os.listdir(DOWNLOAD_FOLDER):
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            
            # Check if file is older than 30 seconds
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > 30:  # 30 seconds
                    try:
                        os.remove(filepath)
                        cleanup_count += 1
                        print(f"🧹 Cleaned up old file: {filename}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete {filename}: {e}")
        
        if cleanup_count > 0:
            print(f"✅ Cleanup complete: Removed {cleanup_count} old file(s)")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def schedule_cleanup():
    """Schedule cleanup to run every 30 seconds"""
    cleanup_old_downloads()
    from threading import Timer
    Timer(30, schedule_cleanup).start()  # Run every 30 seconds

if __name__ == '__main__':
    # Print banner
    print_banner()
    
    print("\n" + "=" * 60)
    print("👨‍💻 Developer: dr1p7.steez")
    print(f"📁 Download folder: {DOWNLOAD_FOLDER}")
    print("\n🌐 Supports 1000+ websites including:")
    print("   • YouTube, Vimeo, TikTok, Twitter, Instagram, Facebook")
    print("   • Twitch, Reddit, Dailymotion, and many more!")
    print("=" * 60)
    
    # Start cleanup scheduler
    print("🧹 Starting automatic cleanup scheduler (runs every hour)")
    schedule_cleanup()
    
    # Get port from environment variable (for cloud deployment) or use default
    port = int(os.environ.get('PORT', Config.PORT))
    
    print(f"🚀 Server starting on port {port}")
    print(f"   Open your browser and navigate to the URL above")
    print("=" * 60 + "\n")
    
    # Run in production mode (debug=False for security)
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)

