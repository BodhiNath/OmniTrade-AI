"""
Configuration management for OmniTrade AI
"""
from typing import Optional, List
import secrets
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "OmniTrade AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="JWT secret key - MUST be set in production"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v, info):
        """Validate SECRET_KEY is set properly in production"""
        if info.data.get('ENVIRONMENT') == 'production' and len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters in production. "
                "Generate one with: openssl rand -hex 32"
            )
        return v
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    INFLUXDB_URL: str = Field(default="http://localhost:8086")
    INFLUXDB_TOKEN: Optional[str] = None
    INFLUXDB_ORG: str = "omnitrade"
    INFLUXDB_BUCKET: str = "trading_data"
    
    # Broker APIs - Alpaca (Stocks)
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"  # Use paper trading by default
    ALPACA_LIVE_MODE: bool = False
    
    # Broker APIs - Binance (Crypto)
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    BINANCE_TESTNET: bool = True  # Use testnet by default
    
    # Market Data
    FINNHUB_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    
    # AI/ML
    OPENAI_API_KEY: Optional[str] = None
    
    # Risk Management
    MAX_POSITION_SIZE_PCT: float = 5.0  # Max 5% per position
    MAX_PORTFOLIO_EXPOSURE_PCT: float = 80.0  # Max 80% total exposure
    DEFAULT_STOP_LOSS_PCT: float = 2.0  # 2% stop loss
    DAILY_LOSS_LIMIT_PCT: float = 10.0  # Halt trading after 10% daily loss
    MAX_CONSECUTIVE_LOSSES: int = 5  # Pause after 5 consecutive losses
    
    # Trading
    ENABLE_TRADING: bool = False  # Manual enable required
    TRADING_HOURS_ONLY: bool = True  # Only trade during market hours
    MIN_ORDER_SIZE_USD: float = 10.0
    MAX_OPEN_POSITIONS: int = 20
    
    # Notifications
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    ALERT_EMAIL: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

