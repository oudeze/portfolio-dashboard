"""
P&L calculation endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PnLSummary
from app.providers.factory import create_provider
from app.services.position_tracker import PositionTracker

router = APIRouter()

# Singleton provider instance
_provider = None


def get_provider():
    """Get or create provider instance."""
    global _provider
    if _provider is None:
        _provider = create_provider()
    return _provider


@router.get("/daily", response_model=List[PnLSummary])
async def get_daily_pnl(db: Session = Depends(get_db)):
    """
    Get daily P&L summary for all positions.
    Calculates unrealized P&L using current market prices.
    
    Args:
        db: Database session
        
    Returns:
        List of P&L summaries by symbol
    """
    tracker = PositionTracker(db)
    positions = tracker.list_positions()
    
    provider = get_provider()
    summaries = []
    
    for position in positions:
        try:
            # Get current price
            quote = await provider.get_quote(position.symbol)
            current_price = quote.price
            
            # Calculate unrealized P&L
            cost_basis = position.qty * position.avg_price
            current_value = position.qty * current_price
            unrealized_pnl = current_value - cost_basis
            
            # Total P&L
            total_pnl = position.realized_pnl + unrealized_pnl
            
            summary = PnLSummary(
                symbol=position.symbol,
                qty=position.qty,
                avg_price=position.avg_price,
                current_price=current_price,
                unrealized_pnl=round(unrealized_pnl, 2),
                realized_pnl=round(position.realized_pnl, 2),
                total_pnl=round(total_pnl, 2)
            )
            
            summaries.append(summary)
        
        except Exception as e:
            # If quote not available, skip or use zero
            print(f"Warning: Could not get quote for {position.symbol}: {e}")
            continue
    
    return summaries

