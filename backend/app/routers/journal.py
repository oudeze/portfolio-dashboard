"""
Trade journal endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JournalEntry
from app.services.journal_storage import JournalStorage
from app.services.position_tracker import PositionTracker

router = APIRouter()


class CreateJournalEntryRequest(BaseModel):
    """Request model for creating a journal entry."""
    symbol: str
    side: str  # buy or sell
    qty: float
    price: float
    notes: Optional[str] = None


@router.post("", response_model=JournalEntry, status_code=201)
async def create_journal_entry(
    request: CreateJournalEntryRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new journal entry.
    Also updates position and calculates realized P&L.
    
    Args:
        request: Journal entry creation request
        db: Database session
        
    Returns:
        Created journal entry
    """
    # Validate side
    if request.side not in ["buy", "sell"]:
        raise HTTPException(
            status_code=400,
            detail="Side must be 'buy' or 'sell'"
        )
    
    # Create journal entry
    storage = JournalStorage(db)
    entry = storage.create(
        symbol=request.symbol,
        side=request.side,
        qty=request.qty,
        price=request.price,
        notes=request.notes
    )
    
    # Update position
    try:
        tracker = PositionTracker(db)
        tracker.process_trade(entry)
    except ValueError as e:
        # Position error, but journal entry was created
        raise HTTPException(status_code=400, detail=str(e))
    
    return entry


@router.get("", response_model=List[JournalEntry])
async def list_journal_entries(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(100, description="Maximum number of entries"),
    db: Session = Depends(get_db)
):
    """
    List journal entries.
    
    Args:
        symbol: Optional symbol filter
        limit: Maximum number of entries
        db: Database session
        
    Returns:
        List of journal entries
    """
    storage = JournalStorage(db)
    return storage.list(symbol=symbol, limit=limit)


@router.get("/{entry_id}", response_model=JournalEntry)
async def get_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Get journal entry by ID.
    
    Args:
        entry_id: Entry ID
        db: Database session
        
    Returns:
        Journal entry
    """
    storage = JournalStorage(db)
    entry = storage.get(entry_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete journal entry.
    
    Note: This does not reverse position changes. Use with caution.
    
    Args:
        entry_id: Entry ID
        db: Database session
    """
    storage = JournalStorage(db)
    deleted = storage.delete(entry_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Journal entry not found")

