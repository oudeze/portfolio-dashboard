"""
Paper trading order endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.alpaca_client import AlpacaClient
from app.services.journal_storage import JournalStorage

router = APIRouter()

# Global Alpaca client
alpaca_client = AlpacaClient()


class CreateOrderRequest(BaseModel):
    """Request model for creating an order."""
    symbol: str
    side: str  # buy or sell
    qty: float
    order_type: str = "market"


class OrderResponse(BaseModel):
    """Response model for order creation."""
    order_id: str
    symbol: str
    side: str
    qty: float
    status: str
    filled_qty: Optional[float] = None
    filled_avg_price: Optional[float] = None


@router.post("", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    db: Session = Depends(get_db)
):
    """
    Create a paper trading order via Alpaca.
    If paper trading is disabled, simulates the order and adds to journal.
    
    Args:
        request: Order creation request
        db: Database session
        
    Returns:
        Order response
    """
    # Validate side
    if request.side not in ["buy", "sell"]:
        raise HTTPException(
            status_code=400,
            detail="Side must be 'buy' or 'sell'"
        )
    
    try:
        if alpaca_client._is_configured():
            # Create real order via Alpaca
            order = await alpaca_client.create_order(
                symbol=request.symbol,
                side=request.side,
                qty=request.qty,
                order_type=request.order_type
            )
            
            # Get filled details
            filled_qty = float(order.get("filled_qty", 0))
            filled_avg_price = float(order.get("filled_avg_price", 0))
            
            # Add to journal if filled
            if filled_qty > 0:
                storage = JournalStorage(db)
                storage.create(
                    symbol=request.symbol,
                    side=request.side,
                    qty=filled_qty,
                    price=filled_avg_price,
                    notes=f"Alpaca paper order {order.get('id')}"
                )
            
            return OrderResponse(
                order_id=order.get("id", ""),
                symbol=order.get("symbol", request.symbol),
                side=order.get("side", request.side),
                qty=float(order.get("qty", request.qty)),
                status=order.get("status", "new"),
                filled_qty=filled_qty if filled_qty > 0 else None,
                filled_avg_price=filled_avg_price if filled_avg_price > 0 else None
            )
        else:
            # Simulate order (for testing without Alpaca)
            raise HTTPException(
                status_code=400,
                detail="Paper trading not enabled. Set PAPER_TRADING_ENABLED=true and configure Alpaca credentials."
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.get("/{order_id}", response_model=dict)
async def get_order_status(order_id: str):
    """
    Get order status from Alpaca.
    
    Args:
        order_id: Order ID
        
    Returns:
        Order status
    """
    if not alpaca_client._is_configured():
        raise HTTPException(
            status_code=400,
            detail="Paper trading not enabled"
        )
    
    try:
        order = await alpaca_client.get_order_status(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order status: {str(e)}")

