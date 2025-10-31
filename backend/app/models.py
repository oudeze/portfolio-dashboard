"""
Pydantic models for market data.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Symbol(BaseModel):
    """Symbol/ticker model."""
    symbol: str = Field(..., description="Ticker symbol (e.g., BTCUSDT, AAPL)")
    name: Optional[str] = Field(None, description="Human-readable name")
    asset_type: str = Field(default="crypto", description="Asset type: crypto, equity, etc.")


class Quote(BaseModel):
    """Quote/price model."""
    symbol: str = Field(..., description="Ticker symbol")
    price: float = Field(..., description="Current price")
    ts: str = Field(..., description="Timestamp in ISO format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "price": 43250.50,
                "ts": "2024-01-01T12:00:00Z"
            }
        }


class AlertRule(BaseModel):
    """Alert rule model."""
    id: str = Field(..., description="Unique alert ID")
    symbol: str = Field(..., description="Ticker symbol to monitor")
    kind: str = Field(..., description="Alert type: price_above, price_below, pct_move")
    threshold: float = Field(..., description="Threshold value")
    enabled: bool = Field(default=True, description="Whether alert is enabled")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert_123",
                "symbol": "BTCUSDT",
                "kind": "price_above",
                "threshold": 50000.0,
                "enabled": True
            }
        }

