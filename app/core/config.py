from pydantic_settings import BaseSettings
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Storee API"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend development server
        "http://127.0.0.1:3000",  # Frontend development server (alternative)
    ]
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_KEY: str  # Anon key
    SUPABASE_SERVICE_KEY: str | None = None  # Service role key (optional)
    SUPABASE_JWT_SECRET: str
    
    # OpenAI settings
    OPENAI_API_KEY: str
    
    # Storage settings
    MEDIA_BUCKET: str = "media"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS from environment if it exists
        if "CORS_ORIGINS" in kwargs:
            try:
                # Try to parse as JSON first
                self.CORS_ORIGINS = json.loads(kwargs["CORS_ORIGINS"])
            except json.JSONDecodeError:
                # If not valid JSON, try to parse as comma-separated string
                self.CORS_ORIGINS = [origin.strip() for origin in kwargs["CORS_ORIGINS"].split(",")]

settings = Settings()

# Log configuration on startup
logger.info("Loading configuration...")
logger.info(f"Supabase URL: {settings.SUPABASE_URL}")
logger.info(f"Supabase Key: {settings.SUPABASE_KEY[:10]}...")
