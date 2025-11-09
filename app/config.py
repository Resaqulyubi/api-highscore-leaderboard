from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "sqlite:///./highscore.db"
    
    # API
    api_title: str = "HighScore API"
    api_version: str = "1.0.0"
    api_description: str = "Open-source leaderboard API for games"
    
    # CORS
    cors_origins: str = "*"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 6400
    
    # Security Settings
    enable_rate_limiting: bool = True
    enable_security_headers: bool = True
    enable_request_logging: bool = True
    max_request_size: int = 1048576  # 1MB in bytes
    
    # Rate Limiting (requests per time period)
    rate_limit_create_game: str = "5/hour"
    rate_limit_submit_score: str = "100/minute"
    rate_limit_get_leaderboard: str = "60/minute"
    rate_limit_default: str = "100/minute"
    
    # API Key Settings
    api_key_min_length: int = 32
    api_key_max_age_days: int = 365  # Optional: implement key expiration
    
    # Input Validation
    max_player_name_length: int = 50
    max_game_name_length: int = 100
    max_description_length: int = 500
    max_score_value: int = 999999999
    max_metadata_size: int = 10240  # 10KB for metadata JSON
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
