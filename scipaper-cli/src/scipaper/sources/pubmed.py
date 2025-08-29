from typing import Any, Dict, List, Optional
import httpx


class PubMedSource:
    name = "pubmed"

    async def search(self, query: str, limit: int, filters: Optional[dict] = None) -> List[Dict[str, Any]]:
        # Use E-utilities esearch to get ids then esummary to fetch details
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={"db": "pubmed", "retmode": "json", "retmax": limit, "term": query},
            )
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return []
            r2 = await c.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "pubmed", "retmode": "json", "id": ",".join(ids)},
            )
            r2.raise_for_status()
            summaries = r2.json().get("result", {})
        out: List[Dict[str, Any]] = []
        for pid in ids:
            s = summaries.get(pid) or {}
            title = s.get("title")
            authors = []
            for a in s.get("authors", []) or []:
                if isinstance(a, dict):
                    nm = a.get("name") or " ".join(filter(None, [a.get("authtype"), a.get("name")]))
                    if nm:
                        authors.append(nm)
            date = s.get("pubdate")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
            out.append({
                "id": pid,
                "title": title,
                "authors": authors,
                "date": date,
                "doi": s.get("elocationid") if s.get("elocationid", "").startswith("10.") else None,
                "url": url,
                "source": self.name,
            })
        return out


