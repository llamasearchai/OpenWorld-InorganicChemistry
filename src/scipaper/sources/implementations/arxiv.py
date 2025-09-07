"""arXiv data source implementation using the arxiv Python package."""

from typing import Any, Optional

import asyncio
from loguru import logger

from ..base_source import BaseSource


class ArxivSource(BaseSource):
    name = "arxiv"

    async def search(self, query: str, limit: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        try:
            import arxiv  # type: ignore

            def sync_search():
                search = arxiv.Search(query=query, max_results=limit)
                results: list[dict[str, Any]] = []
                for r in search.results():
                    authors = [a.name for a in getattr(r, "authors", [])]
                    results.append(
                        {
                            "id": r.get_short_id() if hasattr(r, "get_short_id") else r.entry_id,
                            "title": r.title,
                            "authors": authors,
                            "date": str(getattr(r, "published", ""))[:10],
                            "abstract": r.summary,
                            "journal": "",
                            "doi": getattr(r, "doi", "") or "",
                            "url": r.pdf_url or r.entry_id,
                            "source": "arxiv",
                        }
                    )
                return results

            results = await asyncio.to_thread(sync_search)
            return results
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return []

    async def fetch(self, identifier: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        try:
            import arxiv  # type: ignore

            def sync_fetch():
                # Try to search by id for a single result
                search = arxiv.Search(id_list=[identifier])
                for r in search.results():
                    authors = [a.name for a in getattr(r, "authors", [])]
                    return {
                        "id": r.get_short_id() if hasattr(r, "get_short_id") else r.entry_id,
                        "title": r.title,
                        "authors": authors,
                        "date": str(getattr(r, "published", ""))[:10],
                        "abstract": r.summary,
                        "journal": "",
                        "doi": getattr(r, "doi", "") or "",
                        "url": r.pdf_url or r.entry_id,
                        "source": "arxiv",
                    }
                return None

            result = await asyncio.to_thread(sync_fetch)
            return result
        except Exception as e:
            logger.error(f"arXiv fetch failed: {e}")
            return None

