from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List, Optional

import requests


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str


def _search_duckduckgo(query: str, max_results: int, timeout: int) -> List[WebResult]:
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    out: List[WebResult] = []
    # Prefer explicit results if present
    for item in data.get("Results", [])[:max_results]:
        out.append(WebResult(title=item.get("Text", ""), url=item.get("FirstURL", ""), snippet=item.get("Text", "")))
    if len(out) < max_results:
        # Fallback to RelatedTopics
        for item in data.get("RelatedTopics", []):
            if isinstance(item, dict) and "FirstURL" in item:
                out.append(WebResult(title=item.get("Text", ""), url=item.get("FirstURL", ""), snippet=item.get("Text", "")))
                if len(out) >= max_results:
                    break
            elif isinstance(item, dict) and "Topics" in item:
                for sub in item.get("Topics", []):
                    if len(out) >= max_results:
                        break
                    out.append(WebResult(title=sub.get("Text", ""), url=sub.get("FirstURL", ""), snippet=sub.get("Text", "")))
    return out


def _search_tavily(query: str, max_results: int, timeout: int) -> List[WebResult]:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return []
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {"query": query, "max_results": max_results}
    r = requests.post(url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    out: List[WebResult] = []
    for item in data.get("results", [])[:max_results]:
        out.append(WebResult(title=item.get("title", ""), url=item.get("url", ""), snippet=item.get("content", "")))
    return out


def _search_serpapi(query: str, max_results: int, timeout: int) -> List[WebResult]:
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        return []
    url = "https://serpapi.com/search.json"
    params = {"q": query, "engine": "google", "api_key": api_key, "num": max_results}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    out: List[WebResult] = []
    for item in data.get("organic_results", [])[:max_results]:
        out.append(WebResult(title=item.get("title", ""), url=item.get("link", ""), snippet=item.get("snippet", "")))
    return out


def web_search(query: str, provider: Optional[str] = None, max_results: int = 5, timeout: int = 20) -> List[WebResult]:
    provider = (provider or "auto").lower()
    # Provider selection: explicit > env-based > duckduckgo
    if provider == "tavily" or (provider == "auto" and os.environ.get("TAVILY_API_KEY")):
        results = _search_tavily(query, max_results, timeout)
        if results:
            return results
    if provider == "serpapi" or (provider == "auto" and os.environ.get("SERPAPI_API_KEY")):
        results = _search_serpapi(query, max_results, timeout)
        if results:
            return results
    # Default to DuckDuckGo instant answers fallback
    return _search_duckduckgo(query, max_results, timeout)


