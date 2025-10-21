# Utility functions for AnyVideo Downloader
# Developer: dr1p7.steez

import os
import re
from datetime import datetime
from typing import Optional, Dict, Any

def format_bytes(bytes_value: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    if bytes_value == 0:
        return '0 Bytes'
    
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    k = 1024
    i = 0
    
    while bytes_value >= k and i < len(sizes) - 1:
        bytes_value /= k
        i += 1
    
    return f"{bytes_value:.2f} {sizes[i]}"


def format_duration(seconds: int) -> str:
    """
    Convert seconds to human-readable duration.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1:23:45" or "12:34")
    """
    if not seconds or seconds == 0:
        return '0:00'
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for all operating systems
    """
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename or 'download'


def validate_url(url: str) -> bool:
    """
    Validate if the string is a proper URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def get_file_extension(format_type: str, quality: str = 'best') -> str:
    """
    Get appropriate file extension based on format and quality.
    
    Args:
        format_type: 'video' or 'audio'
        quality: Quality setting
        
    Returns:
        File extension (e.g., 'mp4', 'mp3')
    """
    if format_type == 'audio':
        return 'mp3'
    return 'mp4'


def calculate_eta(downloaded: int, total: int, speed: float) -> Optional[int]:
    """
    Calculate estimated time remaining for download.
    
    Args:
        downloaded: Bytes downloaded so far
        total: Total bytes to download
        speed: Current download speed in bytes/sec
        
    Returns:
        Estimated seconds remaining, or None if cannot calculate
    """
    if not speed or speed <= 0 or total <= downloaded:
        return None
    
    remaining = total - downloaded
    return int(remaining / speed)


def get_quality_label(height: int) -> str:
    """
    Convert video height to quality label.
    
    Args:
        height: Video height in pixels
        
    Returns:
        Quality label (e.g., "1080p", "4K")
    """
    if height >= 2160:
        return "4K"
    elif height >= 1440:
        return "2K"
    elif height >= 1080:
        return "1080p"
    elif height >= 720:
        return "720p"
    elif height >= 480:
        return "480p"
    elif height >= 360:
        return "360p"
    else:
        return f"{height}p"


def format_timestamp(iso_string: str) -> str:
    """
    Convert ISO timestamp to readable format.
    
    Args:
        iso_string: ISO 8601 timestamp string
        
    Returns:
        Formatted date/time string
    """
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return iso_string


def clean_title(title: str) -> str:
    """
    Clean video title for display.
    
    Args:
        title: Original video title
        
    Returns:
        Cleaned title
    """
    # Remove excessive whitespace
    title = ' '.join(title.split())
    
    # Limit length for display
    max_length = 100
    if len(title) > max_length:
        title = title[:max_length - 3] + '...'
    
    return title


def parse_quality_string(quality_str: str) -> Dict[str, Any]:
    """
    Parse quality string to extract details.
    
    Args:
        quality_str: Quality string (e.g., "1080p", "best", "4k")
        
    Returns:
        Dictionary with quality details
    """
    quality_str = quality_str.lower()
    
    if quality_str == 'best':
        return {'type': 'best', 'height': None}
    elif '4k' in quality_str or '2160' in quality_str:
        return {'type': '4k', 'height': 2160}
    elif '1080' in quality_str:
        return {'type': '1080p', 'height': 1080}
    elif '720' in quality_str:
        return {'type': '720p', 'height': 720}
    elif '480' in quality_str:
        return {'type': '480p', 'height': 480}
    else:
        return {'type': quality_str, 'height': None}


def check_disk_space(path: str, required_bytes: int) -> bool:
    """
    Check if there's enough disk space available.
    
    Args:
        path: Directory path to check
        required_bytes: Required space in bytes
        
    Returns:
        True if enough space available, False otherwise
    """
    try:
        stat = os.statvfs(path) if hasattr(os, 'statvfs') else None
        if stat:
            available = stat.f_bavail * stat.f_frsize
            return available >= required_bytes
    except (OSError, AttributeError):
        pass
    
    # If we can't check, assume there's enough space
    return True


def get_file_info(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary with file information or None if file doesn't exist
    """
    if not os.path.exists(filepath):
        return None
    
    stat = os.stat(filepath)
    return {
        'name': os.path.basename(filepath),
        'size': stat.st_size,
        'size_formatted': format_bytes(stat.st_size),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
    }


def create_progress_bar(progress: float, width: int = 50) -> str:
    """
    Create a text-based progress bar.
    
    Args:
        progress: Progress percentage (0-100)
        width: Width of the progress bar in characters
        
    Returns:
        Progress bar string
    """
    filled = int(width * progress / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f'[{bar}] {progress:.1f}%'


def estimate_download_time(file_size: int, speed: float) -> str:
    """
    Estimate total download time.
    
    Args:
        file_size: Total file size in bytes
        speed: Download speed in bytes/sec
        
    Returns:
        Formatted time estimate
    """
    if not speed or speed <= 0:
        return 'Unknown'
    
    seconds = file_size / speed
    return format_duration(int(seconds))


# Console colors for terminal output
class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        """Disable colors (for Windows compatibility)"""
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.RED = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


def print_banner():
    """Print application banner"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   {Colors.BOLD}█████╗ ███╗   ██╗██╗   ██╗██╗   ██╗██╗██████╗ ███████╗ ██████╗{Colors.ENDC}{Colors.CYAN}  ║
║  {Colors.BOLD}██╔══██╗████╗  ██║╚██╗ ██╔╝██║   ██║██║██╔══██╗██╔════╝██╔═══██╗{Colors.ENDC}{Colors.CYAN} ║
║  {Colors.BOLD}███████║██╔██╗ ██║ ╚████╔╝ ██║   ██║██║██║  ██║█████╗  ██║   ██║{Colors.ENDC}{Colors.CYAN} ║
║  {Colors.BOLD}██╔══██║██║╚██╗██║  ╚██╔╝  ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║{Colors.ENDC}{Colors.CYAN} ║
║  {Colors.BOLD}██║  ██║██║ ╚████║   ██║    ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝{Colors.ENDC}{Colors.CYAN} ║
║  {Colors.BOLD}╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝     ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝{Colors.ENDC}{Colors.CYAN}  ║
║                                                               ║
║          {Colors.GREEN}Download videos from 1000+ websites{Colors.ENDC}{Colors.CYAN}              ║
║                   {Colors.YELLOW}Version 1.0.0{Colors.ENDC}{Colors.CYAN}                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)


if __name__ == '__main__':
    # Test utilities
    print("Testing utility functions...\n")
    
    print(f"Format bytes: {format_bytes(1536000000)}")
    print(f"Format duration: {format_duration(3725)}")
    print(f"Sanitize filename: {sanitize_filename('My <Video>: Test|File?.mp4')}")
    print(f"Validate URL: {validate_url('https://www.youtube.com/watch?v=test')}")
    print(f"Get quality label: {get_quality_label(1080)}")
    print(f"Progress bar: {create_progress_bar(65.5)}")
    
    print("\n" + "=" * 60)
    print_banner()

