"""
Core Package - Urbain Sustainability System
Configuration, sécurité, base de données et dépendances
"""

from .config import settings
from .database import Base, engine, AsyncSessionLocal, get_db, init_db, close_db
from .security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token,
    verify_token, authenticate_user, PermissionChecker
)
from .exceptions import (
    UrbainException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ExternalServiceError,
    DatabaseError,
    FileUploadError,
    BusinessLogicError,
    ServiceUnavailableError,
    InvalidStateError
)

__all__ = [
    "settings",
    "Base", "engine", "AsyncSessionLocal", "get_db", "init_db", "close_db",
    "verify_password", "get_password_hash",
    "create_access_token", "create_refresh_token",
    "verify_token", "authenticate_user", "PermissionChecker",
    "UrbainException",
    "AuthenticationError", "AuthorizationError",
    "ValidationError", "NotFoundError", "ConflictError",
    "RateLimitError", "ExternalServiceError",
    "DatabaseError", "FileUploadError",
    "BusinessLogicError", "ServiceUnavailableError", "InvalidStateError"
]
