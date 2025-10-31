"""
Position tracking and P&L calculation service.
"""

from datetime import datetime, timezone
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.db_models import JournalEntryDB, PositionDB
from app.models import JournalEntry, Position


class PositionTracker:
    """
    Tracks positions and calculates P&L.
    Uses FIFO average price method.
    """
    
    def __init__(self, db: Session):
        """Initialize position tracker with database session."""
        self.db = db
    
    def process_trade(self, entry: JournalEntry) -> Position:
        """
        Process a trade entry and update position.
        
        Args:
            entry: Journal entry
            
        Returns:
            Updated position
        """
        # Get or create position
        position = self.db.query(PositionDB).filter(
            PositionDB.symbol == entry.symbol
        ).first()
        
        if not position:
            # Create new position
            position = PositionDB(
                symbol=entry.symbol,
                qty=0.0,
                avg_price=0.0,
                realized_pnl=0.0
            )
            self.db.add(position)
        
        if entry.side == "buy":
            # Buy: increase position, update average price
            old_qty = position.qty
            old_avg = position.avg_price
            
            new_qty = old_qty + entry.qty
            
            if new_qty > 0:
                # Calculate new average price
                total_cost = (old_qty * old_avg) + (entry.qty * entry.price)
                new_avg = total_cost / new_qty
                
                position.qty = new_qty
                position.avg_price = new_avg
            
        elif entry.side == "sell":
            # Sell: decrease position, calculate realized P&L
            if position.qty <= 0:
                # No position to sell
                raise ValueError(f"Cannot sell {entry.symbol}: no position")
            
            sell_qty = min(entry.qty, position.qty)
            remaining_qty = position.qty - sell_qty
            
            # Calculate realized P&L
            cost_basis = sell_qty * position.avg_price
            proceeds = sell_qty * entry.price
            realized = proceeds - cost_basis
            
            position.realized_pnl += realized
            position.qty = remaining_qty
            
            # If position fully closed, reset average price
            if remaining_qty == 0:
                position.avg_price = 0.0
        
        self.db.commit()
        self.db.refresh(position)
        
        return self._db_to_model(position)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Position or None if not found
        """
        position = self.db.query(PositionDB).filter(
            PositionDB.symbol == symbol
        ).first()
        
        if not position:
            return None
        
        return self._db_to_model(position)
    
    def list_positions(self) -> list[Position]:
        """
        List all positions with non-zero quantity.
        
        Returns:
            List of positions
        """
        positions = self.db.query(PositionDB).filter(
            PositionDB.qty != 0.0
        ).all()
        
        return [self._db_to_model(pos) for pos in positions]
    
    @staticmethod
    def _db_to_model(db_position: PositionDB) -> Position:
        """Convert database model to Pydantic model."""
        return Position(
            symbol=db_position.symbol,
            qty=db_position.qty,
            avg_price=db_position.avg_price,
            realized_pnl=db_position.realized_pnl
        )

