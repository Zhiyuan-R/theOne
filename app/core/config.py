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
    database_path: str = "./theone_production.db"
    database_url: str = "sqlite:///./theone_production.db"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override database_url if database_path is set via environment
        if os.getenv("DATABASE_PATH"):
            self.database_path = os.getenv("DATABASE_PATH")
            self.database_url = f"sqlite:///{self.database_path}"
            # Ensure database directory exists
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)

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
    uploads_path: str = "./static/uploads"  # Can be overridden by UPLOADS_PATH env var
    allowed_image_extensions: set = {".jpg", ".jpeg", ".png", ".webp"}
    allowed_audio_extensions: set = {".mp3", ".wav", ".m4a"}

    def get_upload_dir(self):
        """Get upload directory, checking environment variable first"""
        return os.getenv("UPLOADS_PATH", self.upload_dir)

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

# Create upload directories if they don't exist
upload_base_dir = settings.get_upload_dir()
os.makedirs(upload_base_dir, exist_ok=True)
os.makedirs(f"{upload_base_dir}/profiles", exist_ok=True)
os.makedirs(f"{upload_base_dir}/expectations", exist_ok=True)
os.makedirs(f"{upload_base_dir}/ideal_partners", exist_ok=True)
os.makedirs(f"{upload_base_dir}/audio", exist_ok=True)
