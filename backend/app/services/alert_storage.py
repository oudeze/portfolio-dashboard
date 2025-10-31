"""
In-memory alert storage.
"""

import uuid
from typing import Dict, List, Optional

from app.models import AlertRule


class AlertStorage:
    """
    In-memory storage for alert rules.
    Will be replaced with database in Phase 4.
    """
    
    def __init__(self):
        """Initialize alert storage."""
        self._alerts: Dict[str, AlertRule] = {}
    
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
        alert = AlertRule(
            id=alert_id,
            symbol=symbol,
            kind=kind,
            threshold=threshold,
            enabled=enabled
        )
        self._alerts[alert_id] = alert
        return alert
    
    def get(self, alert_id: str) -> Optional[AlertRule]:
        """
        Get alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert rule or None if not found
        """
        return self._alerts.get(alert_id)
    
    def list(self, symbol: Optional[str] = None) -> List[AlertRule]:
        """
        List all alerts, optionally filtered by symbol.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of alert rules
        """
        alerts = list(self._alerts.values())
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol]
        return alerts
    
    def update(self, alert_id: str, **kwargs) -> Optional[AlertRule]:
        """
        Update alert rule.
        
        Args:
            alert_id: Alert ID
            **kwargs: Fields to update
            
        Returns:
            Updated alert rule or None if not found
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(alert, key):
                setattr(alert, key, value)
        
        return alert
    
    def delete(self, alert_id: str) -> bool:
        """
        Delete alert rule.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if deleted, False if not found
        """
        if alert_id in self._alerts:
            del self._alerts[alert_id]
            return True
        return False
    
    def get_by_symbol(self, symbol: str) -> List[AlertRule]:
        """
        Get all enabled alerts for a symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            List of enabled alert rules
        """
        return [
            alert for alert in self._alerts.values()
            if alert.symbol == symbol and alert.enabled
        ]


# Global storage instance
alert_storage = AlertStorage()

