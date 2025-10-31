"""
Alpaca Paper Trading client.
"""

import aiohttp
from typing import Optional

from app.config import settings


class AlpacaClient:
    """
    Client for Alpaca Paper Trading API.
    """
    
    def __init__(self):
        """Initialize Alpaca client."""
        self.api_key_id = settings.ALPACA_API_KEY_ID
        self.api_secret = settings.ALPACA_API_SECRET_KEY
        self.base_url = settings.ALPACA_PAPER_BASE_URL
        self.enabled = settings.PAPER_TRADING_ENABLED
    
    def _is_configured(self) -> bool:
        """Check if Alpaca is configured."""
        return bool(self.api_key_id and self.api_secret and self.enabled)
    
    def _get_headers(self) -> dict:
        """Get request headers with authentication."""
        return {
            "APCA-API-KEY-ID": self.api_key_id,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Content-Type": "application/json"
        }
    
    async def create_order(
        self,
        symbol: str,
        side: str,  # buy or sell
        qty: float,
        order_type: str = "market"
    ) -> dict:
        """
        Create a market order.
        
        Args:
            symbol: Ticker symbol
            side: Order side (buy or sell)
            qty: Quantity
            order_type: Order type (default: market)
            
        Returns:
            Order response from Alpaca
        """
        if not self._is_configured():
            raise ValueError("Alpaca paper trading not configured or enabled")
        
        url = f"{self.base_url}/v2/orders"
        
        payload = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "qty": str(qty),
            "time_in_force": "day"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise ValueError(f"Alpaca API error: {response.status} - {error}")
    
    async def get_order_status(self, order_id: str) -> dict:
        """
        Get order status.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status from Alpaca
        """
        if not self._is_configured():
            raise ValueError("Alpaca paper trading not configured or enabled")
        
        url = f"{self.base_url}/v2/orders/{order_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise ValueError(f"Alpaca API error: {response.status} - {error}")

