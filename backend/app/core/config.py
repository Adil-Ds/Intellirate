import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # App Info
    APP_NAME: str = "IntelliRate Gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"
    
    # SageMaker Endpoints
    ISOLATION_FOREST_ENDPOINT_NAME: str = ""
    XGBOOST_ENDPOINT_NAME: str = ""
    PROPHET_ENDPOINT_NAME: str = ""
    
    # S3 Storage
    S3_BUCKET_NAME: str = "intellirate-ml-models"
    S3_MODEL_PREFIX: str = "models/v1/"
    
    # ML Service Configuration
    USE_CLOUD_ML: bool = True
    ML_PREDICTION_TIMEOUT: int = 5
    ML_RETRY_ATTEMPTS: int = 3
    ML_RETRY_BACKOFF: int = 2
    
    # Fallback Configuration
    ENABLE_ML_FALLBACK: bool = True
    FALLBACK_WARNING_THRESHOLD: float = 0.7
    
    # Caching
    ML_PREDICTION_CACHE_TTL: int = 300
    ML_FEATURES_CACHE_TTL: int = 60
    
    # Monitoring
    CLOUD_ML_HEALTH_CHECK_INTERVAL: int = 60
    LOG_CLOUD_ML_REQUESTS: bool = True
    TRACK_CLOUD_ML_LATENCY: bool = True
    
    # ============ GROQ API CONFIGURATION ============
    GROQ_API_KEY: str = ""
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    
    # ============ FIREBASE CONFIGURATION ============
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    
    # ============ RATE LIMITING ============
    # Hourly-based rate limits
    RATE_LIMIT_FREE: int = 50          # requests per hour
    RATE_LIMIT_PRO: int = 1000         # requests per hour
    RATE_LIMIT_ENTERPRISE: int = -1    # unlimited (-1 means no limit)
    RATE_LIMIT_WINDOW_SECONDS: int = 3600  # 1 hour = 3600 seconds
    
    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
