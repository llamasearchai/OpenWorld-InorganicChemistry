from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

import requests

USER_AGENT = "OpenInorganicChemistry/1.0 (+https://example.org)"


@dataclass
class Paper:
    title: str
    authors: list[str]
    year: Optional[int]
    url: str
    source: str


def search_arxiv(query: str, max_results: int = 5) -> List[Paper]:
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
    }
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    text = r.text
    entries = text.split("<entry>")
    out: List[Paper] = []
    for e in entries[1:]:
        title = _extract(e, "title")
        link = _extract_link(e)
        authors = _extract_authors(e)
        year = _extract_year(e)
        out.append(Paper(title=title.strip(), authors=authors, year=year, url=link, source="arXiv"))
    return out


def _extract(xml: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", xml, flags=re.S)
    return (m.group(1) if m else "").strip()


def _extract_link(xml: str) -> str:
    m = re.search(r'<link[^>]+href="([^"]+)"', xml)
    return m.group(1) if m else ""


def _extract_authors(xml: str) -> list[str]:
    return re.findall(r"<name>(.*?)</name>", xml)


def _extract_year(xml: str) -> Optional[int]:
    m = re.search(r"<published>(\d{4})-\d{2}-\d{2}", xml)
    return int(m.group(1)) if m else None

# PubMed integration intentionally omitted to keep dependencies minimal for offline testing


def search_crossref(query: str, max_results: int = 5) -> List[Paper]:
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": max_results, "select": "title,author,URL,created"}
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    out: List[Paper] = []
    for item in data.get("message", {}).get("items", []):
        title = item.get("title", [""])[0]
        url_item = item.get("URL", "")
        authors = [f"{a.get('given','')} {a.get('family','')}".strip() for a in item.get("author", [])]
        year = None
        created = item.get("created", {}).get("date-parts", [])
        if created and created[0] and len(created[0]) >= 1:
            year = int(created[0][0])
        out.append(Paper(title=title, authors=authors, year=year, url=url_item, source="Crossref"))
    return out


