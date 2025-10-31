"""
Configuration management using environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Provider selection
    DATA_PROVIDER: str = "mock"  # mock | binance | polygon | mixed
    POLYGON_API_KEY: str = ""
    
    # Routing & CORS
    BACKEND_PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    
    # Database
    DATABASE_URL: str = "sqlite:///./market.db"
    
    # Alerts
    SLACK_WEBHOOK_URL: str = ""
    
    # Optional paper trading
    PAPER_TRADING_ENABLED: bool = False
    ALPACA_API_KEY_ID: str = ""
    ALPACA_API_SECRET_KEY: str = ""
    ALPACA_PAPER_BASE_URL: str = "https://paper-api.alpaca.markets"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

