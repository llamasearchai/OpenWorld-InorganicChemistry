"""IEEE Xplore data source implementation using ieeeexplore library."""
from typing import Any, Optional

import asyncio
from loguru import logger

from ...config import settings
from ...exceptions import NetworkError, SourceError
from ..base_source import BaseSource
from ieeeexplore import IeeeExplore


class IeeeSource(BaseSource):
    """IEEE Xplore data source for technical papers."""
    
    name = "ieee"

    async def search(self, query: str, limit: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        """Search for papers using IEEE Xplore."""
        try:
            ieee = IeeeExplore()
            def sync_search():
                results = []
                search_results = ieee.search(query, max_results=limit)
                for result in search_results:
                    authors = [author for author in result.get('authors', [])]
                    year = result.get('publication_year', '')
                    results.append({
                        "id": result.get('paper_id', ''),
                        "title": result.get('title', ''),
                        "authors": authors,
                        "date": str(year) if year else "",
                        "abstract": result.get('abstract', ''),
                        "journal": result.get('journal', ''),
                        "doi": result.get('doi', ''),
                        "url": result.get('url', ''),
                        "source": "ieee",
                    })
                return results

            results = await asyncio.to_thread(sync_search)
            return results
        except Exception as e:
            logger.error(f"IEEE Xplore search failed: {e}")
            raise SourceError(f"IEEE Xplore search failed: {e}")

    async def fetch(self, identifier: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        """Fetch a specific paper by identifier."""
        try:
            ieee = IeeeExplore()
            def sync_fetch():
                # Try to fetch by DOI or ID
                search_results = ieee.search(identifier, max_results=1)
                result = next(search_results, None)
                if result:
                    authors = [author for author in result.get('authors', [])]
                    year = result.get('publication_year', '')
                    return {
                        "id": result.get('paper_id', ''),
                        "title": result.get('title', ''),
                        "authors": authors,
                        "date": str(year) if year else "",
                        "abstract": result.get('abstract', ''),
                        "journal": result.get('journal', ''),
                        "doi": result.get('doi', ''),
                        "url": result.get('url', ''),
                        "source": "ieee",
                    }
                return None

            result = await asyncio.to_thread(sync_fetch)
            return result
        except Exception as e:
            logger.error(f"IEEE Xplore fetch failed: {e}")
            raise SourceError(f"IEEE Xplore fetch failed: {e}")