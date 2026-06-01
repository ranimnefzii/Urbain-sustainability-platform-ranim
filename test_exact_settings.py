import subprocess, sys, json

# Reproduce the EXACT Settings class from config.py
code = r"""
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    APP_NAME: str = "Urbain Sustainability System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/urbain_sustainability"
    DATABASE_TEST_URL: str = "postgresql://username:password@localhost:5432/urbain_sustainability_test"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GOOGLE_MAPS_API_KEY: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@urbain-sustainability.com"
    EMAIL_FROM_NAME: str = "Urbain Sustainability System"
    AI_MODEL_PATH: str = "./models/urban_classifier.pkl"
    AI_CONFIDENCE_THRESHOLD: float = 0.7
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    MAX_FILE_SIZE: int = 10485760
    UPLOAD_DIR: str = "./uploads"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090
    
    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "allow"}

s = Settings()
print('OK')
print('DB:', s.DATABASE_URL[:30])
print('SECRET:', s.SECRET_KEY[:10])
print('ORIGINS:', s.ALLOWED_ORIGINS)
print('SENTRY:', s.SENTRY_DSN)
"""

print("Test: Exact Settings reproduction")
result = subprocess.run(
    [sys.executable, "-c", code],
    capture_output=True, text=True, timeout=30,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)
