from typing import Any, Dict, List, Optional
from .base_source import BaseSource
import arxiv
import asyncio
from datetime import datetime


class ArxivSource(BaseSource):

    name = "arxiv"

    async def search(self, query: str, limit: int,
                     filters: Optional[dict] = None) -> List[Dict[str, Any]]:
        def _do():
            # Use the newer client factory for future compatibility
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=arxiv.SortCriterion.SubmittedDate)
            out = []
            for r in client.results(search):
                out.append({
                    "id": r.entry_id.split("/")[-1].split("v")[0],
                    "title": r.title,
                    "authors": [a.name for a in r.authors],
                    "date": r.published.strftime("%Y-%m-%d") if isinstance(r.published, datetime) else None,
                    "abstract": r.summary,
                    "journal": r.journal_ref or "arXiv",
                    "doi": getattr(r, "doi", None),
                    "url": r.pdf_url,
                    "categories": list(getattr(r, "categories", []) or []),
                    "source": "arxiv",
                })
            return out
        return await asyncio.to_thread(_do)
