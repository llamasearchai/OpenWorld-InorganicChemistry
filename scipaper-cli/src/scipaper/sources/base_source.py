from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseSource(ABC):

    name: str = "base"

    @abstractmethod
    async def search(self, query: str, limit: int,
                     filters: Optional[dict] = None) -> List[Dict[str, Any]]:
        ...
