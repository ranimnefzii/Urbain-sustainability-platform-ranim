"""
Constants - Urbain Sustainability System
Constantes partagées dans toute l'application
"""


class ErrorCodes:
    """Error codes for the application"""
    # Authentication
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_INVALID = "AUTH_INVALID"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    AUTH_DISABLED = "AUTH_DISABLED"
    
    # Authorization
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_FIELD = "MISSING_FIELD"
    
    # Resources
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    
    # Business
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INVALID_STATE = "INVALID_STATE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    
    # External
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    
    # System
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    FILE_UPLOAD_ERROR = "FILE_UPLOAD_ERROR"


class SignalConstants:
    """Constants for signal processing"""
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 5000
    MIN_TITLE_LENGTH = 5
    MIN_DESCRIPTION_LENGTH = 10
    MAX_IMAGES_PER_SIGNAL = 5
    MAX_FILE_SIZE_MB = 10
    REFERENCE_PREFIX = "SIG"
    DEFAULT_SEARCH_RADIUS_KM = 5


class PaginationDefaults:
    """Default pagination values"""
    DEFAULT_PAGE = 1
    DEFAULT_SIZE = 20
    MAX_SIZE = 100
    DEFAULT_SORT = "created_at"
    DEFAULT_ORDER = "desc"


class NotificationDefaults:
    """Default notification configuration"""
    MAX_RETRIES = 3
    RETRY_DELAY_MINUTES = 5
    MAX_BATCH_SIZE = 100
    DEFAULT_PRIORITY = "normal"
    EXPIRY_DAYS = 30


class FileUploadDefaults:
    """File upload configuration"""
    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'text/plain', 'application/msword']
    MAX_IMAGE_SIZE_MB = 5
    MAX_DOCUMENT_SIZE_MB = 20
    THUMBNAIL_SIZE = (200, 200)
    UPLOAD_PATH_IMAGES = "uploads/images/"
    UPLOAD_PATH_DOCUMENTS = "uploads/documents/"


class CacheDefaults:
    """Cache configuration"""
    SIGNAL_TTL = 300
    USER_TTL = 600
    CATEGORY_TTL = 3600
    REPORT_TTL = 1800
    STATS_TTL = 300
    PREFIX_SIGNAL = "signal:"
    PREFIX_USER = "user:"
    PREFIX_CATEGORY = "category:"
    PREFIX_STATS = "stats:"


class StatusMessages:
    """Status message templates"""
    SIGNAL_CREATED = "Signalement {ref} créé avec succès"
    SIGNAL_UPDATED = "Signalement {ref} mis à jour"
    SIGNAL_ASSIGNED = "Signalement {ref} assigné au secteur"
    SIGNAL_RESOLVED = "Signalement {ref} marqué comme résolu"
    USER_REGISTERED = "Compte créé avec succès. Vérifiez votre email."
    USER_UPDATED = "Profil mis à jour avec succès"
    PASSWORD_CHANGED = "Mot de passe modifié avec succès"
    REPORT_GENERATED = "Rapport généré avec succès"
    NOTIFICATION_SENT = "Notification envoyée avec succès"
