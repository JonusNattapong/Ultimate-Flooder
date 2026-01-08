"""
Security utilities for input validation and safe operations
"""
import re
import ipaddress
from urllib.parse import urlparse
import socket

def validate_url(url, allow_private=False):
    """
    Validate URL to prevent SSRF attacks
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Only allow http/https
        if parsed.scheme not in ['http', 'https']:
            return False

        # Validate hostname/IP
        hostname = parsed.hostname
        if not hostname:
            return False

        # Check if it's a valid IP or hostname
        try:
            ipaddress.ip_address(hostname)
            is_ip = True
        except ValueError:
            is_ip = False

        if is_ip:
            ip = ipaddress.ip_address(hostname)
            # Block private IPs unless explicitly allowed
            if not allow_private and ip.is_private:
                return False
            # Block loopback
            if ip.is_loopback:
                return False
        else:
            # Validate hostname format
            if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', hostname):
                return False

        return True
    except Exception:
        return False

def validate_ip(ip_str):
    """
    Validate IP address
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        # Block private and loopback IPs
        if ip.is_private or ip.is_loopback:
            return False
        return True
    except ValueError:
        return False

def sanitize_input(input_str, max_length=1000):
    """
    Sanitize user input to prevent injection attacks
    """
    if not input_str or not isinstance(input_str, str):
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;&|`$()<>]', '', input_str)

    # Limit length
    return sanitized[:max_length]

def safe_request_headers(base_headers=None):
    """
    Generate safe request headers
    """
    headers = base_headers or {}
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
        'Upgrade-Insecure-Requests': '1',
    })
    return headers

def rate_limit_check(key, max_calls=10, time_window=60):
    """
    Simple rate limiting (in-memory, not persistent)
    """
    import time
    if not hasattr(rate_limit_check, 'calls'):
        rate_limit_check.calls = {}

    current_time = time.time()

    if key not in rate_limit_check.calls:
        rate_limit_check.calls[key] = []

    # Clean old calls
    rate_limit_check.calls[key] = [
        call_time for call_time in rate_limit_check.calls[key]
        if current_time - call_time < time_window
    ]

    if len(rate_limit_check.calls[key]) >= max_calls:
        return False

    rate_limit_check.calls[key].append(current_time)
    return True

def safe_file_write(filepath, content, max_size=1048576):  # 1MB limit
    """
    Safe file writing with size limits
    """
    if len(content) > max_size:
        raise ValueError(f"Content too large: {len(content)} > {max_size}")

    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)