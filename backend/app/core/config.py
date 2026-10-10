"""
Configuration Settings for Urbain Sustainability System
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Configuration
    APP_NAME: str = "Urbain Sustainability System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/urbain_sustainability"
    DATABASE_TEST_URL: str = "postgresql://username:password@localhost:5432/urbain_sustainability_test"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT Configuration
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = ""
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@urbain-sustainability.com"
    EMAIL_FROM_NAME: str = "Urbain Sustainability System"
    
    # AI Model Configuration
    AI_MODEL_PATH: str = "./models/urban_classifier.pkl"
    AI_CONFIDENCE_THRESHOLD: float = 0.7
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090
    
    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "allow"}


# Create global settings instance
settings = Settings()
