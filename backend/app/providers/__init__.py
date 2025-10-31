"""
Data provider package.
"""

from app.providers.base import IDataProvider
from app.providers.mock import MockProvider

__all__ = ["IDataProvider", "MockProvider"]

