"""
Mock data provider with random walk price generation.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import AsyncIterator, List

from app.models import Quote, Symbol
from app.providers.base import IDataProvider


class MockProvider(IDataProvider):
    """
    Mock provider that generates random walk prices.
    """
    
    def __init__(self):
        """Initialize mock provider with default symbols."""
        # Starting prices for symbols
        self._prices: dict[str, float] = {
            "BTCUSDT": 43000.0,
            "ETHUSDT": 2500.0,
            "SOLUSDT": 100.0,
            "AAPL": 175.0,
            "MSFT": 380.0,
            "GOOGL": 140.0,
        }
        
        # Symbol metadata
        self._symbols = [
            Symbol(symbol="BTCUSDT", name="Bitcoin", asset_type="crypto"),
            Symbol(symbol="ETHUSDT", name="Ethereum", asset_type="crypto"),
            Symbol(symbol="SOLUSDT", name="Solana", asset_type="crypto"),
            Symbol(symbol="AAPL", name="Apple Inc.", asset_type="equity"),
            Symbol(symbol="MSFT", name="Microsoft Corp.", asset_type="equity"),
            Symbol(symbol="GOOGL", name="Alphabet Inc.", asset_type="equity"),
        ]
    
    async def list_symbols(self) -> List[Symbol]:
        """List available symbols."""
        return self._symbols.copy()
    
    async def get_quote(self, symbol: str) -> Quote:
        """
        Get latest quote for a symbol.
        Generates a small random walk from last price.
        """
        if symbol not in self._prices:
            # Initialize price if symbol not seen before
            self._prices[symbol] = random.uniform(10.0, 1000.0)
        
        # Random walk: change by up to 0.5% up or down
        change_pct = random.uniform(-0.005, 0.005)
        self._prices[symbol] *= (1 + change_pct)
        
        return Quote(
            symbol=symbol,
            price=round(self._prices[symbol], 2),
            ts=datetime.now(timezone.utc).isoformat()
        )
    
    async def stream(self, subscriptions: List[str]) -> AsyncIterator[Quote]:
        """
        Stream quotes for subscribed symbols.
        Emits a new quote every second with random walk prices.
        """
        while True:
            for symbol in subscriptions:
                quote = await self.get_quote(symbol)
                yield quote
            
            # Wait 1 second before next batch
            await asyncio.sleep(1)

