"""
Factory for creating data providers based on configuration.
"""

from app.config import settings
from app.providers.base import IDataProvider
from app.providers.mock import MockProvider


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
        # Will be implemented in Phase 2
        raise NotImplementedError("Binance provider not yet implemented")
    elif provider_type == "polygon":
        # Will be implemented in Phase 5
        raise NotImplementedError("Polygon provider not yet implemented")
    elif provider_type == "mixed":
        # Will be implemented in Phase 5
        raise NotImplementedError("Mixed provider not yet implemented")
    else:
        # Default to mock
        return MockProvider()

