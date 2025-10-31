"""
Alert management endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models import AlertRule
from app.services.alert_storage import alert_storage
from app.services.slack_notifier import SlackNotifier

router = APIRouter()

# Global notifier instance
notifier = SlackNotifier()


class CreateAlertRequest(BaseModel):
    """Request model for creating an alert."""
    symbol: str
    kind: str  # price_above, price_below, pct_move
    threshold: float
    enabled: bool = True


class UpdateAlertRequest(BaseModel):
    """Request model for updating an alert."""
    enabled: Optional[bool] = None
    threshold: Optional[float] = None


@router.post("", response_model=AlertRule, status_code=201)
async def create_alert(request: CreateAlertRequest):
    """
    Create a new alert rule.
    
    Args:
        request: Alert creation request
        
    Returns:
        Created alert rule
    """
    # Validate alert kind
    valid_kinds = ["price_above", "price_below", "pct_move"]
    if request.kind not in valid_kinds:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid alert kind. Must be one of: {valid_kinds}"
        )
    
    alert = alert_storage.create(
        symbol=request.symbol,
        kind=request.kind,
        threshold=request.threshold,
        enabled=request.enabled
    )
    
    return alert


@router.get("", response_model=List[AlertRule])
async def list_alerts(
    symbol: Optional[str] = Query(None, description="Filter by symbol")
):
    """
    List all alert rules.
    
    Args:
        symbol: Optional symbol filter
        
    Returns:
        List of alert rules
    """
    return alert_storage.list(symbol=symbol)


@router.get("/{alert_id}", response_model=AlertRule)
async def get_alert(alert_id: str):
    """
    Get alert by ID.
    
    Args:
        alert_id: Alert ID
        
    Returns:
        Alert rule
    """
    alert = alert_storage.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}", response_model=AlertRule)
async def update_alert(alert_id: str, request: UpdateAlertRequest):
    """
    Update alert rule.
    
    Args:
        alert_id: Alert ID
        request: Update request
        
    Returns:
        Updated alert rule
    """
    alert = alert_storage.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Build update dict
    updates = {}
    if request.enabled is not None:
        updates["enabled"] = request.enabled
    if request.threshold is not None:
        updates["threshold"] = request.threshold
    
    updated = alert_storage.update(alert_id, **updates)
    return updated


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(alert_id: str):
    """
    Delete alert rule.
    
    Args:
        alert_id: Alert ID
    """
    deleted = alert_storage.delete(alert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/{alert_id}/test", status_code=200)
async def test_alert(alert_id: str):
    """
    Test alert by sending a test notification.
    
    Args:
        alert_id: Alert ID
    """
    alert = alert_storage.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Send test notification
    success = await notifier.send_test_alert()
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to send test notification. Check Slack webhook configuration."
        )
    
    return {"message": "Test alert sent successfully"}

