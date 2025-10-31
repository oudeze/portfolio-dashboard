"""
Database-backed alert storage.
"""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import AlertRule
from app.db_models import AlertRuleDB


class AlertStorage:
    """
    Database storage for alert rules.
    """
    
    def __init__(self, db: Session):
        """Initialize alert storage with database session."""
        self.db = db
    
    def create(self, symbol: str, kind: str, threshold: float, enabled: bool = True) -> AlertRule:
        """
        Create a new alert rule.
        
        Args:
            symbol: Ticker symbol
            kind: Alert type (price_above, price_below, pct_move)
            threshold: Threshold value
            enabled: Whether alert is enabled
            
        Returns:
            Created alert rule
        """
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"
        db_alert = AlertRuleDB(
            id=alert_id,
            symbol=symbol,
            kind=kind,
            threshold=threshold,
            enabled=enabled
        )
        self.db.add(db_alert)
        self.db.commit()
        self.db.refresh(db_alert)
        
        return self._db_to_model(db_alert)
    
    def get(self, alert_id: str) -> Optional[AlertRule]:
        """
        Get alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert rule or None if not found
        """
        db_alert = self.db.query(AlertRuleDB).filter(AlertRuleDB.id == alert_id).first()
        if not db_alert:
            return None
        return self._db_to_model(db_alert)
    
    def list(self, symbol: Optional[str] = None) -> List[AlertRule]:
        """
        List all alerts, optionally filtered by symbol.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of alert rules
        """
        query = self.db.query(AlertRuleDB)
        if symbol:
            query = query.filter(AlertRuleDB.symbol == symbol)
        
        db_alerts = query.all()
        return [self._db_to_model(alert) for alert in db_alerts]
    
    def update(self, alert_id: str, **kwargs) -> Optional[AlertRule]:
        """
        Update alert rule.
        
        Args:
            alert_id: Alert ID
            **kwargs: Fields to update
            
        Returns:
            Updated alert rule or None if not found
        """
        db_alert = self.db.query(AlertRuleDB).filter(AlertRuleDB.id == alert_id).first()
        if not db_alert:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(db_alert, key):
                setattr(db_alert, key, value)
        
        self.db.commit()
        self.db.refresh(db_alert)
        
        return self._db_to_model(db_alert)
    
    def delete(self, alert_id: str) -> bool:
        """
        Delete alert rule.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if deleted, False if not found
        """
        db_alert = self.db.query(AlertRuleDB).filter(AlertRuleDB.id == alert_id).first()
        if not db_alert:
            return False
        
        self.db.delete(db_alert)
        self.db.commit()
        return True
    
    def get_by_symbol(self, symbol: str) -> List[AlertRule]:
        """
        Get all enabled alerts for a symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            List of enabled alert rules
        """
        db_alerts = self.db.query(AlertRuleDB).filter(
            AlertRuleDB.symbol == symbol,
            AlertRuleDB.enabled == True
        ).all()
        return [self._db_to_model(alert) for alert in db_alerts]
    
    @staticmethod
    def _db_to_model(db_alert: AlertRuleDB) -> AlertRule:
        """Convert database model to Pydantic model."""
        return AlertRule(
            id=db_alert.id,
            symbol=db_alert.symbol,
            kind=db_alert.kind,
            threshold=db_alert.threshold,
            enabled=db_alert.enabled
        )

