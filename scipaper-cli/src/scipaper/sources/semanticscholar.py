from typing import Any, Dict, List, Optional
import asyncio
import httpx


class SemanticScholarSource:
    name = "semanticscholar"

    async def search(self, query: str, limit: int, filters: Optional[dict] = None) -> List[Dict[str, Any]]:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        fields = "title,year,authors,externalIds,url,openAccessPdf"
        params = {"query": query, "limit": limit, "fields": fields}
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(url, params=params)
            rs = r.raise_for_status()
            if asyncio.iscoroutine(rs):
                await rs
            dj = r.json()
            data = await dj if asyncio.iscoroutine(dj) else dj
        out: List[Dict[str, Any]] = []
        for it in data.get("data", []) or []:
            title = it.get("title")
            doi = None
            ext = it.get("externalIds") or {}
            if isinstance(ext, dict):
                doi = ext.get("DOI")
            authors = [a.get("name") for a in (it.get("authors") or []) if isinstance(a, dict)]
            pdf_url = None
            oap = it.get("openAccessPdf") or {}
            if isinstance(oap, dict):
                pdf_url = oap.get("url")
            out.append({
                "id": doi or it.get("paperId") or it.get("url") or title,
                "title": title,
                "authors": authors,
                "date": str(it.get("year")) if it.get("year") else None,
                "doi": doi,
                "url": pdf_url or it.get("url"),
                "source": self.name,
            })
        return out


