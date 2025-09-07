"""Base class for all data source implementations."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseSource(ABC):
    """Abstract base class for data sources."""

    name: str = "base"

    @abstractmethod
    async def search(self, query: str, limit: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        """Search for papers."""
        raise NotImplementedError

    @abstractmethod
    async def fetch(self, identifier: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        """Fetch a specific paper by its identifier."""
        raise NotImplementedError
