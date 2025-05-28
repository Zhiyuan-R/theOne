"""
Configuration settings for theOne dating app
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Configuration
    app_name: str = "theOne"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./theone.db"

    # Authentication
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    gpt_model: str = "gpt-4o-mini"  # Updated to GPT-4o-mini for cost efficiency
    embedding_model: str = "text-embedding-3-small"  # Updated to OpenAI embedding model

    # File Upload Configuration
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./static/uploads"
    allowed_image_extensions: set = {".jpg", ".jpeg", ".png", ".webp"}
    allowed_audio_extensions: set = {".mp3", ".wav", ".m4a"}

    # Server Configuration (for Docker deployment)
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 2

    # CORS Configuration
    cors_origins: str = "*"

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "/var/log/theone.log"

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(f"{settings.upload_dir}/profiles", exist_ok=True)
os.makedirs(f"{settings.upload_dir}/expectations", exist_ok=True)
os.makedirs(f"{settings.upload_dir}/audio", exist_ok=True)
