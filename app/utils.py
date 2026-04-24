"""
Utility functions for URL Shortener
QR Code generation, URL validation, and helpers
"""
import string
import random
import segno
from io import BytesIO
from urllib.parse import urlparse
from datetime import datetime


SHORTCODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits + "-_"
RESERVED_CODES = {"admin", "api", "webhook", "stats", "info", "shorten", "qr", "analytics"}


def generate_shortcode(length=SHORTCODE_LENGTH) -> str:
    """Generate random shortcode"""
    return ''.join(random.choices(ALPHABET, k=length))


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def is_valid_custom_alias(alias: str) -> bool:
    """
    Validate custom alias
    - 4-32 characters
    - alphanumeric, hyphen, underscore only
    - not in reserved words
    """
    if not (4 <= len(alias) <= 32):
        return False
    if not all(c in ALPHABET for c in alias):
        return False
    if alias.lower() in RESERVED_CODES:
        return False
    return True


def generate_qr_code(url: str) -> bytes:
    """
    Generate QR code for shortened URL
    Returns PNG bytes
    """
    try:
        qr = segno.make(url, error='H', micro=False)
        buffer = BytesIO()
        qr.save(buffer, kind='png', scale=8)
        return buffer.getvalue()
    except Exception as e:
        print(f"QR Code generation error: {e}")
        return None


def format_analytics(url_record) -> dict:
    """Format URL analytics for display"""
    return {
        "shortcode": url_record.shortcode,
        "custom_alias": url_record.custom_alias,
        "original_url": url_record.original_url,
        "total_clicks": url_record.clicks,
        "last_accessed": url_record.last_accessed.isoformat() if url_record.last_accessed else None,
        "created_at": url_record.created_at.isoformat(),
        "days_active": (datetime.utcnow() - url_record.created_at).days
    }


def sanitize_url(url: str) -> str:
    """Add protocol if missing"""
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url
