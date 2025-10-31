"""
Base interface for data providers.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List

from app.models import Quote, Symbol


class IDataProvider(ABC):
    """Interface for market data providers."""
    
    @abstractmethod
    async def list_symbols(self) -> List[Symbol]:
        """
        List available symbols.
        
        Returns:
            List of available symbols
        """
        pass
    
    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """
        Get latest quote for a symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Latest quote
        """
        pass
    
    @abstractmethod
    async def stream(self, subscriptions: List[str]) -> AsyncIterator[Quote]:
        """
        Stream real-time quotes for subscribed symbols.
        
        Args:
            subscriptions: List of symbols to subscribe to
            
        Yields:
            Quote objects as they arrive
        """
        pass

