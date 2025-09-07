"""Google Scholar data source implementation using scholarly library."""
from typing import Any, Optional

import asyncio
from loguru import logger

from ...config import settings
from ...exceptions import NetworkError, SourceError
from ..base_source import BaseSource
from scholarly import scholarly


class GoogleScholarSource(BaseSource):
    """Google Scholar data source for academic papers."""
    
    name = "googlescholar"

    async def search(self, query: str, limit: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        """Search for papers using Google Scholar."""
        try:
            def sync_search():
                search_query = scholarly.search_pubs(query)
                results = []
                for i, result in enumerate(search_query):
                    if i >= limit:
                        break
                    authors = [author for author in result.get('author', [])]
                    year = result.get('bib', {}).get('pub_year', '')
                    results.append({
                        "id": result.get('pub_id', ''),
                        "title": result.get('bib', {}).get('title', ''),
                        "authors": authors,
                        "date": str(year) if year else "",
                        "abstract": result.get('bib', {}).get('abstract', ''),
                        "journal": result.get('bib', {}).get('venue', ''),
                        "doi": result.get('bib', {}).get('doi', ''),
                        "url": result.get('eprint_url', '') or result.get('pub_url', ''),
                        "source": "googlescholar",
                    })
                return results

            results = await asyncio.to_thread(sync_search)
            return results
        except Exception as e:
            logger.error(f"Google Scholar search failed: {e}")
            raise SourceError(f"Google Scholar search failed: {e}")

    async def fetch(self, identifier: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        """Fetch a specific paper by identifier."""
        try:
            def sync_fetch():
                # Try to fetch by title or ID
                search_query = scholarly.search_pubs(identifier)
                result = next(search_query, None)
                if result:
                    authors = [author for author in result.get('author', [])]
                    year = result.get('bib', {}).get('pub_year', '')
                    return {
                        "id": result.get('pub_id', ''),
                        "title": result.get('bib', {}).get('title', ''),
                        "authors": authors,
                        "date": str(year) if year else "",
                        "abstract": result.get('bib', {}).get('abstract', ''),
                        "journal": result.get('bib', {}).get('venue', ''),
                        "doi": result.get('bib', {}).get('doi', ''),
                        "url": result.get('eprint_url', '') or result.get('pub_url', ''),
                        "source": "googlescholar",
                    }
                return None

            result = await asyncio.to_thread(sync_fetch)
            return result
        except Exception as e:
            logger.error(f"Google Scholar fetch failed: {e}")
            raise SourceError(f"Google Scholar fetch failed: {e}")