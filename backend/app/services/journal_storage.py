"""
Journal entry storage.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import JournalEntry
from app.db_models import JournalEntryDB


class JournalStorage:
    """
    Database storage for journal entries.
    """
    
    def __init__(self, db: Session):
        """Initialize journal storage with database session."""
        self.db = db
    
    def create(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        notes: Optional[str] = None,
        ts: Optional[datetime] = None
    ) -> JournalEntry:
        """
        Create a new journal entry.
        
        Args:
            symbol: Ticker symbol
            side: Trade side (buy or sell)
            qty: Quantity
            price: Price
            notes: Optional notes
            ts: Optional timestamp (defaults to now)
            
        Returns:
            Created journal entry
        """
        entry_id = f"journal_{uuid.uuid4().hex[:8]}"
        entry_ts = ts or datetime.now(timezone.utc)
        
        db_entry = JournalEntryDB(
            id=entry_id,
            symbol=symbol,
            side=side,
            qty=qty,
            price=price,
            notes=notes,
            ts=entry_ts
        )
        
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        
        return self._db_to_model(db_entry)
    
    def get(self, entry_id: str) -> Optional[JournalEntry]:
        """
        Get journal entry by ID.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Journal entry or None if not found
        """
        db_entry = self.db.query(JournalEntryDB).filter(
            JournalEntryDB.id == entry_id
        ).first()
        
        if not db_entry:
            return None
        
        return self._db_to_model(db_entry)
    
    def list(self, symbol: Optional[str] = None, limit: int = 100) -> List[JournalEntry]:
        """
        List journal entries, optionally filtered by symbol.
        
        Args:
            symbol: Optional symbol filter
            limit: Maximum number of entries to return
            
        Returns:
            List of journal entries (most recent first)
        """
        query = self.db.query(JournalEntryDB)
        
        if symbol:
            query = query.filter(JournalEntryDB.symbol == symbol)
        
        db_entries = query.order_by(JournalEntryDB.ts.desc()).limit(limit).all()
        
        return [self._db_to_model(entry) for entry in db_entries]
    
    def delete(self, entry_id: str) -> bool:
        """
        Delete journal entry.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            True if deleted, False if not found
        """
        db_entry = self.db.query(JournalEntryDB).filter(
            JournalEntryDB.id == entry_id
        ).first()
        
        if not db_entry:
            return False
        
        self.db.delete(db_entry)
        self.db.commit()
        
        return True
    
    @staticmethod
    def _db_to_model(db_entry: JournalEntryDB) -> JournalEntry:
        """Convert database model to Pydantic model."""
        return JournalEntry(
            id=db_entry.id,
            ts=db_entry.ts.isoformat(),
            symbol=db_entry.symbol,
            side=db_entry.side,
            qty=db_entry.qty,
            price=db_entry.price,
            notes=db_entry.notes
        )

