"""
SQLAlchemy database models.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime
from sqlalchemy.sql import func

from app.database import Base


class AlertRuleDB(Base):
    """Alert rule database model."""
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    kind = Column(String, nullable=False)  # price_above, price_below, pct_move
    threshold = Column(Float, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class JournalEntryDB(Base):
    """Trade journal entry database model."""
    __tablename__ = "journal"
    
    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)  # buy, sell
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    ts = Column(DateTime, default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class PositionDB(Base):
    """Position database model."""
    __tablename__ = "positions"
    
    symbol = Column(String, primary_key=True, index=True)
    qty = Column(Float, nullable=False, default=0.0)
    avg_price = Column(Float, nullable=False, default=0.0)
    realized_pnl = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

