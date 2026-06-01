"""
Validators - Urbain Sustainability System
Fonctions de validation personnalisées
"""

import re
from typing import Optional
from app.core.exceptions import ValidationError


def validate_email(email: str) -> str:
    """Validate and normalize email address"""
    if not email:
        raise ValidationError("Email is required")
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    if len(email) > 255:
        raise ValidationError("Email too long (max 255 characters)")
    return email


def validate_password(password: str) -> str:
    """Validate password strength"""
    if not password:
        raise ValidationError("Password is required")
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    if len(password) > 128:
        raise ValidationError("Password too long (max 128 characters)")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain an uppercase letter")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain a lowercase letter")
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain a digit")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain a special character")
    return password


def validate_phone(phone: str) -> str:
    """Validate phone number"""
    if not phone:
        raise ValidationError("Phone number is required")
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    pattern = r'^\+?[1-9]\d{6,14}$'
    if not re.match(pattern, cleaned):
        raise ValidationError("Invalid phone number format")
    return cleaned


def validate_url(url: str) -> str:
    """Validate URL"""
    if not url:
        raise ValidationError("URL is required")
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url):
        raise ValidationError("Invalid URL format")
    if len(url) > 2048:
        raise ValidationError("URL too long (max 2048 characters)")
    return url


def validate_image_file(filename: str) -> bool:
    """Validate image file extension"""
    allowed = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed:
        raise ValidationError(f"Invalid image format. Allowed: {', '.join(allowed)}")
    return True


def validate_coordinates_range(latitude: float, longitude: float) -> None:
    """Validate geographic coordinates"""
    if not -90 <= latitude <= 90:
        raise ValidationError("Latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise ValidationError("Longitude must be between -180 and 180")


def validate_text_length(text: str, min_len: int = 1, max_len: int = 5000, field_name: str = "Text") -> None:
    """Validate text length"""
    if not text:
        raise ValidationError(f"{field_name} is required")
    if len(text) < min_len:
        raise ValidationError(f"{field_name} must be at least {min_len} characters")
    if len(text) > max_len:
        raise ValidationError(f"{field_name} must not exceed {max_len} characters")


def validate_reference_number(ref: str) -> bool:
    """Validate reference number format"""
    pattern = r'^[A-Z]{3}-\d{6}-[A-Z0-9]{4,8}$'
    return bool(re.match(pattern, ref))


def sanitize_string(text: str, max_length: int = 5000) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'<[^>]+>', '', text)
    return text[:max_length]


def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID string"""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str.lower()))
