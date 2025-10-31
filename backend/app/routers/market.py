"""
Market data endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import Quote, Symbol
from app.providers.factory import create_provider

router = APIRouter()

# Singleton provider instance
_provider = None


def get_provider():
    """Get or create provider instance."""
    global _provider
    if _provider is None:
        _provider = create_provider()
    return _provider


@router.get("/symbols", response_model=List[Symbol])
async def list_symbols():
    """
    List all available symbols.
    
    Returns:
        List of available symbols
    """
    provider = get_provider()
    return await provider.list_symbols()


@router.get("/quotes/latest", response_model=Quote)
async def get_latest_quote(
    symbol: str = Query(..., description="Ticker symbol (e.g., BTCUSDT, AAPL)")
):
    """
    Get latest quote for a symbol.
    
    Args:
        symbol: Ticker symbol to get quote for
        
    Returns:
        Latest quote for the symbol
    """
    provider = get_provider()
    try:
        return await provider.get_quote(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quote: {str(e)}")

