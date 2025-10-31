"""
Mixed provider that routes crypto to Binance WS and equities to Polygon REST.
"""

from typing import AsyncIterator, List

from app.models import Quote, Symbol
from app.providers.base import IDataProvider
from app.providers.binance import BinanceProvider
from app.providers.polygon import PolygonProvider


class MixedProvider(IDataProvider):
    """
    Mixed provider that combines Binance WebSocket (crypto) and Polygon REST (equities).
    Routes symbols ending with USDT to Binance, others to Polygon.
    """
    
    def __init__(self):
        """Initialize mixed provider."""
        self.binance_provider = BinanceProvider()
        self.polygon_provider = PolygonProvider()
    
    async def list_symbols(self) -> List[Symbol]:
        """List all available symbols from both providers."""
        binance_symbols = await self.binance_provider.list_symbols()
        polygon_symbols = await self.polygon_provider.list_symbols()
        return binance_symbols + polygon_symbols
    
    async def get_quote(self, symbol: str) -> Quote:
        """
        Get latest quote for a symbol.
        Routes to appropriate provider based on symbol format.
        """
        if symbol.endswith("USDT"):
            # Crypto: use Binance
            return await self.binance_provider.get_quote(symbol)
        else:
            # Equity: use Polygon
            return await self.polygon_provider.get_quote(symbol)
    
    async def stream(self, subscriptions: List[str]) -> AsyncIterator[Quote]:
        """
        Stream quotes for subscribed symbols.
        Routes crypto to Binance WebSocket, equities to Polygon polling.
        """
        # Separate symbols by type
        crypto_symbols = [s for s in subscriptions if s.endswith("USDT")]
        equity_symbols = [s for s in subscriptions if not s.endswith("USDT")]
        
        # Stream crypto from Binance
        crypto_task = None
        if crypto_symbols:
            import asyncio
            crypto_task = asyncio.create_task(
                self._stream_crypto(crypto_symbols)
            )
        
        # Stream equities from Polygon
        equity_task = None
        if equity_symbols:
            import asyncio
            equity_task = asyncio.create_task(
                self._stream_equities(equity_symbols)
            )
        
        # Combine streams
        if crypto_task:
            async for quote in self._stream_from_task(crypto_task):
                yield quote
        
        if equity_task:
            async for quote in self._stream_from_task(equity_task):
                yield quote
    
    async def _stream_crypto(self, symbols: List[str]) -> AsyncIterator[Quote]:
        """Stream crypto quotes from Binance."""
        async for quote in self.binance_provider.stream(symbols):
            yield quote
    
    async def _stream_equities(self, symbols: List[str]) -> AsyncIterator[Quote]:
        """Stream equity quotes from Polygon."""
        async for quote in self.polygon_provider.stream(symbols):
            yield quote
    
    async def _stream_from_task(self, task):
        """Helper to stream from async task."""
        try:
            while True:
                quote = await task
                yield quote
        except Exception:
            pass

