from typing import Any, Dict, List, Optional
import asyncio
import httpx


def _extract_date(msg: Dict[str, Any]) -> Optional[str]:
    for key in ("issued", "published-print", "published-online"):
        part = msg.get(key, {})
        parts = part.get("date-parts") or part.get("date_parts")
        if parts and isinstance(parts, list) and parts and parts[0]:
            dp = parts[0]
            if len(dp) >= 3:
                return f"{dp[0]:04d}-{dp[1]:02d}-{dp[2]:02d}"
            if len(dp) == 2:
                return f"{dp[0]:04d}-{dp[1]:02d}-01"
            if len(dp) == 1:
                return f"{dp[0]:04d}"
    return None


class CrossrefSource:
    name = "crossref"

    async def search(self, query: str, limit: int, filters: Optional[dict] = None) -> List[Dict[str, Any]]:
        url = "https://api.crossref.org/works"
        params = {"query": query, "rows": limit}
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(url, params=params)
            rs = r.raise_for_status()
            if asyncio.iscoroutine(rs):
                await rs
            dj = r.json()
            data = await dj if asyncio.iscoroutine(dj) else dj
        items = data.get("message", {}).get("items", [])
        out: List[Dict[str, Any]] = []
        for it in items:
            title_list = it.get("title") or []
            title = title_list[0] if title_list else ""
            authors = [
                " ".join([p.get("given", "").strip(), p.get("family", "").strip()]).strip()
                for p in (it.get("author") or [])
                if isinstance(p, dict)
            ]
            doi = it.get("DOI")
            pdf_url = None
            for link in it.get("link", []) or []:
                if link.get("content-type", "").lower() == "application/pdf":
                    pdf_url = link.get("URL")
                    break
            out.append({
                "id": doi or (it.get("URL") or title),
                "title": title,
                "authors": authors,
                "date": _extract_date(it),
                "doi": doi,
                "url": pdf_url or it.get("URL"),
                "source": self.name,
            })
        return out


