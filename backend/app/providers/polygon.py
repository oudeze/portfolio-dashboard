"""
Polygon REST data provider for equities.
"""

import asyncio
from datetime import datetime, timezone
from typing import AsyncIterator, List

import aiohttp

from app.config import settings
from app.models import Quote, Symbol
from app.providers.base import IDataProvider


class PolygonProvider(IDataProvider):
    """
    Polygon REST provider for equities snapshots.
    Uses REST API with polling (no WebSocket in free tier).
    """
    
    BASE_URL = "https://api.polygon.io"
    
    def __init__(self):
        """Initialize Polygon provider."""
        self.api_key = settings.POLYGON_API_KEY
        
        # Available equity symbols
        self._symbols = [
            Symbol(symbol="AAPL", name="Apple Inc.", asset_type="equity"),
            Symbol(symbol="MSFT", name="Microsoft Corp.", asset_type="equity"),
            Symbol(symbol="GOOGL", name="Alphabet Inc.", asset_type="equity"),
            Symbol(symbol="AMZN", name="Amazon.com Inc.", asset_type="equity"),
            Symbol(symbol="TSLA", name="Tesla Inc.", asset_type="equity"),
            Symbol(symbol="NVDA", name="NVIDIA Corp.", asset_type="equity"),
        ]
        
        # Latest prices cache
        self._latest_prices: dict[str, float] = {}
    
    def _is_configured(self) -> bool:
        """Check if Polygon API key is configured."""
        return bool(self.api_key)
    
    async def list_symbols(self) -> List[Symbol]:
        """List available symbols."""
        return self._symbols.copy()
    
    async def get_quote(self, symbol: str) -> Quote:
        """
        Get latest quote for a symbol using Polygon REST API.
        Uses cached price if available and recent, otherwise fetches from API.
        """
        # If we have a cached price, return it
        if symbol in self._latest_prices:
            return Quote(
                symbol=symbol,
                price=self._latest_prices[symbol],
                ts=datetime.now(timezone.utc).isoformat()
            )
        
        # Otherwise, fetch from Polygon REST API
        if not self._is_configured():
            raise ValueError(f"Polygon API key not configured. Set POLYGON_API_KEY in .env")
        
        async with aiohttp.ClientSession() as session:
            # Use last trade endpoint
            url = f"{self.BASE_URL}/v2/last/trade/{symbol}"
            params = {"apikey": self.api_key}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "OK" and "results" in data:
                        result = data["results"]
                        price = result.get("p", 0)  # Last trade price
                        ts_ms = result.get("t", 0)  # Timestamp in milliseconds
                        
                        if price > 0:
                            # Cache the price
                            self._latest_prices[symbol] = price
                            
                            # Convert timestamp
                            ts = datetime.fromtimestamp(
                                ts_ms / 1000,
                                tz=timezone.utc
                            ).isoformat()
                            
                            return Quote(
                                symbol=symbol,
                                price=round(price, 2),
                                ts=ts
                            )
                
                # Fallback: try ticker snapshot
                url = f"{self.BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "OK" and "ticker" in data:
                            ticker = data["ticker"]
                            day = ticker.get("day", {})
                            price = day.get("c", 0)  # Close price
                            
                            if price > 0:
                                self._latest_prices[symbol] = price
                                ts = datetime.now(timezone.utc).isoformat()
                                
                                return Quote(
                                    symbol=symbol,
                                    price=round(price, 2),
                                    ts=ts
                                )
                
                raise ValueError(f"Failed to fetch quote for {symbol}")
    
    async def stream(self, subscriptions: List[str]) -> AsyncIterator[Quote]:
        """
        Stream quotes for subscribed symbols via polling.
        Polls every 60 seconds to respect rate limits (20 req/min).
        """
        if not self._is_configured():
            # If not configured, yield cached prices or raise error
            for symbol in subscriptions:
                if symbol in self._latest_prices:
                    yield Quote(
                        symbol=symbol,
                        price=self._latest_prices[symbol],
                        ts=datetime.now(timezone.utc).isoformat()
                    )
                await asyncio.sleep(1)
            return
        
        # Poll every 60 seconds (respecting 20 req/min rate limit)
        while True:
            for symbol in subscriptions:
                try:
                    quote = await self.get_quote(symbol)
                    yield quote
                    # Small delay between requests
                    await asyncio.sleep(3)  # 20 requests per minute = ~3 seconds per request
                except Exception as e:
                    print(f"Error fetching Polygon quote for {symbol}: {e}")
                    continue
            
            # Wait 60 seconds before next polling cycle
            await asyncio.sleep(60)

