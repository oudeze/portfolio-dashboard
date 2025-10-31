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


class JournalEntry(BaseModel):
    """Trade journal entry model."""
    id: str = Field(..., description="Unique entry ID")
    ts: str = Field(..., description="Timestamp in ISO format")
    symbol: str = Field(..., description="Ticker symbol")
    side: str = Field(..., description="Trade side: buy or sell")
    qty: float = Field(..., description="Quantity")
    price: float = Field(..., description="Price")
    notes: Optional[str] = Field(None, description="Optional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "journal_123",
                "ts": "2024-01-01T12:00:00Z",
                "symbol": "BTCUSDT",
                "side": "buy",
                "qty": 0.5,
                "price": 43000.0,
                "notes": "Entry point"
            }
        }


class Position(BaseModel):
    """Position model."""
    symbol: str = Field(..., description="Ticker symbol")
    qty: float = Field(..., description="Position quantity")
    avg_price: float = Field(..., description="Average entry price")
    realized_pnl: float = Field(..., description="Realized P&L")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "qty": 0.5,
                "avg_price": 43000.0,
                "realized_pnl": 500.0
            }
        }


class PnLSummary(BaseModel):
    """P&L summary model."""
    symbol: str = Field(..., description="Ticker symbol")
    qty: float = Field(..., description="Position quantity")
    avg_price: float = Field(..., description="Average entry price")
    current_price: float = Field(..., description="Current market price")
    unrealized_pnl: float = Field(..., description="Unrealized P&L")
    realized_pnl: float = Field(..., description="Realized P&L")
    total_pnl: float = Field(..., description="Total P&L (realized + unrealized)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "qty": 0.5,
                "avg_price": 43000.0,
                "current_price": 43500.0,
                "unrealized_pnl": 250.0,
                "realized_pnl": 500.0,
                "total_pnl": 750.0
            }
        }

