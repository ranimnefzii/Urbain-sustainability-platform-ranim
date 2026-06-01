"""
Helpers - Urbain Sustainability System
Fonctions utilitaires partagées
"""

import re
import math
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
from math import radians, sin, cos, sqrt, atan2


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object to string"""
    if not dt:
        return ""
    return dt.strftime(format)


def parse_datetime(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse a datetime string to datetime object"""
    try:
        return datetime.strptime(date_str, format)
    except (ValueError, TypeError):
        return None


def generate_slug(text: str, max_length: int = 100) -> str:
    """Generate a URL-friendly slug from text"""
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:max_length].rstrip('-')


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + suffix


def calculate_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculate distance between two coordinates in km (Haversine)"""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate GPS coordinates"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def build_address_string(
    street: Optional[str] = None,
    city: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None
) -> str:
    """Build a formatted address string"""
    parts = [p for p in [street, city, postal_code, country] if p]
    return ", ".join(parts)


def sanitize_html(text: str) -> str:
    """Remove HTML tags from text"""
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text)


def format_phone_number(phone: str, country_code: str = "+216") -> str:
    """Format phone number with country code"""
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('0'):
        digits = digits[1:]
    if not digits.startswith(country_code.replace('+', '')):
        digits = country_code + digits
    return f"+{digits}"


def validate_phone_format(phone: str) -> bool:
    """Validate phone number format"""
    pattern = r'^\+?[1-9]\d{6,14}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


class Paginator:
    """Utility class for pagination calculations"""
    
    def __init__(self, page: int = 1, size: int = 20, max_size: int = 100):
        self.page = max(1, page)
        self.size = min(max_size, max(1, size))
        self.skip = (self.page - 1) * self.size
    
    def get_metadata(self, total: int) -> Dict[str, Any]:
        pages = max(1, (total + self.size - 1) // self.size)
        return {
            "page": self.page,
            "size": self.size,
            "total": total,
            "pages": pages,
            "has_next": self.page < pages,
            "has_prev": self.page > 1
        }
    
    def get_limit_offset(self):
        return self.size, self.skip
