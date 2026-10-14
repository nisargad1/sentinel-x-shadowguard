import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "SENTINEL-X ShadowGuard"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security & Gateway Config
    HMAC_SECRET_KEY: str = os.getenv("HMAC_SECRET_KEY", "sentinel-x-super-secret-hmac-key-hackathon-2026")
    HMAC_MAX_DRIFT_SECONDS: int = 300  # 5 minutes
    HMAC_ENFORCE: bool = False  # Allows relaxed API testing while supporting strict verification endpoint
    
    # Thresholds
    INTENT_DRIFT_THRESHOLD: float = 0.65  # Minimum similarity score required
    RISK_SCORE_THRESHOLD: int = 60  # Risk score >= 60 triggers BLOCK or DECEPTION
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shadowguard.db")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"  # Allows public access during hackathon evaluation
    ]
    
    # Deception Honeypot Sandbox
    HONEYPOT_ENABLED: bool = True
    
    # Admin / Reset token for demo safety
    DEMO_RESET_TOKEN: str = os.getenv("DEMO_RESET_TOKEN", "shadowguard-reset-authorized-token-2026")

settings = Settings()
