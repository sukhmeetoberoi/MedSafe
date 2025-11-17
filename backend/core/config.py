"""
Configuration settings for MedSummarize backend
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""

    # Basic Configuration
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_VERSION: str = "v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://medsummarize.com"
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./medsummarize.db"
    MONGODB_URL: str = "mongodb://localhost:27017/medsummarize"
    REDIS_URL: str = "redis://localhost:6379"

    # Pinecone (Vector Database)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "medsummarize"

    # AI/ML APIs
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "jpeg", "png", "tiff"]

    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-west-2"
    S3_BUCKET_NAME: str = "medsummarize-uploads"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OCR Settings
    TESSERACT_CMD: Optional[str] = None  # Path to Tesseract executable if not in PATH

    # spaCy Model
    SPACY_MODEL: str = "en_core_web_sm"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/medsummarize.log"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("static", exist_ok=True)