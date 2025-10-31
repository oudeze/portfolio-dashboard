"""
Factory for creating data providers based on configuration.
"""

from app.config import settings
from app.providers.base import IDataProvider
from app.providers.binance import BinanceProvider
from app.providers.mock import MockProvider
from app.providers.mixed import MixedProvider
from app.providers.polygon import PolygonProvider


def create_provider() -> IDataProvider:
    """
    Create data provider based on DATA_PROVIDER setting.
    
    Returns:
        IDataProvider instance
    """
    provider_type = settings.DATA_PROVIDER.lower()
    
    if provider_type == "mock":
        return MockProvider()
    elif provider_type == "binance":
        return BinanceProvider()
    elif provider_type == "polygon":
        return PolygonProvider()
    elif provider_type == "mixed":
        return MixedProvider()
    else:
        # Default to mock
        return MockProvider()

