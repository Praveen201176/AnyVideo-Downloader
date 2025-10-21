"""
Security utilities for AnyVideo Downloader
Developer: dr1p7.steez
"""

import re
import bleach
from urllib.parse import urlparse
from functools import wraps
from flask import request, jsonify
import hashlib
import time

class SecurityValidator:
    """Validates and sanitizes user inputs"""
    
    # Allowed URL schemes
    ALLOWED_SCHEMES = ['http', 'https']
    
    # Maximum URL length
    MAX_URL_LENGTH = 2048
    
    # Blocked patterns (SQL injection, XSS, etc.)
    BLOCKED_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'expression\s*\(',
        r'import\s+',
        r'exec\s*\(',
        r'<iframe',
        r'<embed',
        r'<object',
        r'\.\./\.\.',  # Path traversal
        r'\.\.\\\.\.', # Path traversal Windows
        r'union\s+select',  # SQL injection
        r'drop\s+table',
        r'insert\s+into',
        r'delete\s+from',
        r'update\s+.*set',
        r'--\s*$',  # SQL comment
        r'/\*.*\*/',  # SQL comment
    ]
    
    @staticmethod
    def validate_url(url):
        """
        Validate URL format and security
        
        Args:
            url (str): URL to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not url:
            return False, "URL is required"
        
        # Check length
        if len(url) > SecurityValidator.MAX_URL_LENGTH:
            return False, "URL too long"
        
        # Check for blocked patterns
        url_lower = url.lower()
        for pattern in SecurityValidator.BLOCKED_PATTERNS:
            if re.search(pattern, url_lower, re.IGNORECASE):
                return False, "URL contains suspicious content"
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception:
            return False, "Invalid URL format"
        
        # Check scheme
        if parsed.scheme not in SecurityValidator.ALLOWED_SCHEMES:
            return False, f"Only {', '.join(SecurityValidator.ALLOWED_SCHEMES)} URLs are allowed"
        
        # Check for localhost/private IPs (prevent SSRF)
        hostname = parsed.hostname
        if hostname:
            hostname_lower = hostname.lower()
            
            # Block localhost
            if hostname_lower in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
                return False, "Local URLs are not allowed"
            
            # Block private IP ranges
            if hostname_lower.startswith('192.168.') or \
               hostname_lower.startswith('10.') or \
               hostname_lower.startswith('172.'):
                return False, "Private IP addresses are not allowed"
            
            # Block metadata endpoints
            if '169.254.169.254' in hostname_lower:
                return False, "Metadata endpoints are not allowed"
        
        return True, None
    
    @staticmethod
    def sanitize_string(text, max_length=500):
        """
        Sanitize user input string
        
        Args:
            text (str): Text to sanitize
            max_length (int): Maximum allowed length
            
        Returns:
            str: Sanitized text
        """
        if not text:
            return ""
        
        # Limit length
        text = str(text)[:max_length]
        
        # Remove HTML tags and suspicious content
        text = bleach.clean(text, tags=[], strip=True)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        return text.strip()
    
    @staticmethod
    def validate_quality(quality):
        """
        Validate quality parameter
        
        Args:
            quality (str): Quality setting
            
        Returns:
            tuple: (is_valid, sanitized_quality)
        """
        allowed_qualities = ['best', '4k', '1080p', '720p', '480p']
        
        if not quality:
            return True, 'best'
        
        quality = str(quality).lower().strip()
        
        if quality in allowed_qualities:
            return True, quality
        
        return False, 'best'
    
    @staticmethod
    def validate_format(format_type):
        """
        Validate format parameter
        
        Args:
            format_type (str): Format type
            
        Returns:
            tuple: (is_valid, sanitized_format)
        """
        allowed_formats = ['video', 'audio']
        
        if not format_type:
            return True, 'video'
        
        format_type = str(format_type).lower().strip()
        
        if format_type in allowed_formats:
            return True, format_type
        
        return False, 'video'


class RequestValidator:
    """Validates API requests"""
    
    @staticmethod
    def validate_json_request(required_fields=None):
        """
        Decorator to validate JSON requests
        
        Args:
            required_fields (list): List of required field names
        """
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                # Check if request has JSON
                if not request.is_json:
                    return jsonify({
                        'error': 'Content-Type must be application/json'
                    }), 400
                
                # Get JSON data
                try:
                    data = request.get_json()
                except Exception:
                    return jsonify({
                        'error': 'Invalid JSON format'
                    }), 400
                
                # Check required fields
                if required_fields:
                    missing_fields = [
                        field for field in required_fields 
                        if field not in data or not data[field]
                    ]
                    
                    if missing_fields:
                        return jsonify({
                            'error': f'Missing required fields: {", ".join(missing_fields)}'
                        }), 400
                
                return f(*args, **kwargs)
            
            return wrapped
        return decorator
    
    @staticmethod
    def check_request_size(max_size=1024):
        """
        Check request size to prevent DOS
        
        Args:
            max_size (int): Maximum request size in bytes
        """
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                content_length = request.content_length
                
                if content_length and content_length > max_size:
                    return jsonify({
                        'error': 'Request too large'
                    }), 413
                
                return f(*args, **kwargs)
            
            return wrapped
        return decorator


class AntiAbuse:
    """Anti-abuse mechanisms"""
    
    # Store request timestamps per IP
    _request_log = {}
    
    @staticmethod
    def check_rate_limit(ip, max_requests=10, window=60):
        """
        Simple rate limiting
        
        Args:
            ip (str): Client IP
            max_requests (int): Max requests allowed
            window (int): Time window in seconds
            
        Returns:
            bool: True if allowed, False if rate limited
        """
        current_time = time.time()
        
        if ip not in AntiAbuse._request_log:
            AntiAbuse._request_log[ip] = []
        
        # Clean old requests
        AntiAbuse._request_log[ip] = [
            timestamp for timestamp in AntiAbuse._request_log[ip]
            if current_time - timestamp < window
        ]
        
        # Check rate limit
        if len(AntiAbuse._request_log[ip]) >= max_requests:
            return False
        
        # Add current request
        AntiAbuse._request_log[ip].append(current_time)
        
        return True
    
    @staticmethod
    def generate_request_id():
        """Generate unique request ID for tracking"""
        return hashlib.sha256(
            f"{time.time()}{request.remote_addr}".encode()
        ).hexdigest()[:16]


def secure_headers():
    """Add security headers to response"""
    from flask import make_response
    
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            
            # Security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
            return response
        
        return wrapped
    return decorator


# Obfuscation helpers
class Obfuscator:
    """Simple obfuscation utilities"""
    
    @staticmethod
    def encode_string(s):
        """Encode string to base64-like format"""
        import base64
        return base64.b64encode(s.encode()).decode()
    
    @staticmethod
    def decode_string(s):
        """Decode string from base64-like format"""
        import base64
        try:
            return base64.b64decode(s.encode()).decode()
        except Exception:
            return None
    
    @staticmethod
    def hash_string(s):
        """Create hash of string"""
        return hashlib.sha256(s.encode()).hexdigest()

