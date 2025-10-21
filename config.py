# AnyVideo Downloader Configuration
# Developer: dr1p7.steez

import os

class Config:
    """Configuration settings for AnyVideo Downloader"""
    
    # Application Settings
    APP_NAME = "AnyVideo Downloader"
    VERSION = "1.0.0"
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
    
    # Download Settings
    DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
    
    # yt-dlp Settings - Advanced bypass options
    YTDLP_OPTIONS = {
        # SSL/Certificate bypass
        'nocheckcertificate': True,
        
        # User agent spoofing (latest Chrome)
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # Geo-restriction bypass
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        
        # Extract options
        'extract_flat': False,
        'no_color': True,
        
        # Network settings
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        
        # Headers to bypass restrictions
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        
        # Age restriction bypass
        'age_limit': None,
        
        # Extractor options
        'extractor_retries': 3,
        'extractor_args': {
            'youtube': {
                'skip': ['hls', 'dash'],
                'player_skip': ['webpage', 'configs'],
                'player_client': ['android', 'web'],
            }
        },
        
        # Don't stop on errors
        'ignoreerrors': False,
        'no_warnings': False,
        
        # Try to bypass throttling
        'throttledratelimit': None,
        
        # Verbose for debugging
        'verbose': False,
    }
    
    # Quality Settings
    QUALITY_FORMATS = {
        'best': {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        },
        '4k': {
            'format': 'bestvideo[height>=2160]+bestaudio/best[height>=2160]/best',
            'merge_output_format': 'mp4'
        },
        '1080p': {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
            'merge_output_format': 'mp4'
        },
        '720p': {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
            'merge_output_format': 'mp4'
        },
        '480p': {
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best',
            'merge_output_format': 'mp4'
        }
    }
    
    # Audio Extraction Settings
    AUDIO_FORMAT = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]
    }
    
    # File Naming Template
    OUTPUT_TEMPLATE = '%(title)s.%(ext)s'
    
    # Security Settings
    MAX_DOWNLOAD_SIZE = None  # None = unlimited, or set in bytes
    
    # Feature Flags
    ENABLE_PLAYLIST_DOWNLOAD = True
    ENABLE_SUBTITLE_DOWNLOAD = True
    ENABLE_THUMBNAIL_EMBED = True
    ENABLE_METADATA_EMBED = True
    
    # Advanced Features
    CONCURRENT_DOWNLOADS = 1  # Number of simultaneous downloads
    RETRY_ATTEMPTS = 3
    FRAGMENT_RETRIES = 10
    
    # Proxy Settings (if needed)
    PROXY = None  # Example: 'http://proxy.example.com:8080'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'downloader.log'
    
    @staticmethod
    def init_app():
        """Initialize application directories"""
        if not os.path.exists(Config.DOWNLOAD_FOLDER):
            os.makedirs(Config.DOWNLOAD_FOLDER)

