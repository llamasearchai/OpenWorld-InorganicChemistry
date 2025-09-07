"""Crossref data source implementation."""

from typing import Any, Optional

import httpx
from loguru import logger

from ...config import settings
from ...exceptions import NetworkError, SourceError
from ..base_source import BaseSource


class CrossrefSource(BaseSource):
    """Crossref data source for academic papers."""

    name = "crossref"
    base_url = "https://api.crossref.org"

    def __init__(self):
        super().__init__()
        self.user_agent = settings.crossref_user_agent

    async def search(self, query: str, limit: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        """Search for papers using Crossref API."""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "query": query,
                    "rows": min(limit, 100),  # Crossref max is 100
                    "select": "DOI,title,author,issued,link,container-title,URL"
                }

                headers = {"User-Agent": self.user_agent}
                response = await client.get(
                    f"{self.base_url}/works",
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                if hasattr(response, "raise_for_status"):
                    maybe_coro = response.raise_for_status()
                    if hasattr(maybe_coro, "__await__"):
                        await maybe_coro
                data = response.json()

                papers = []
                for item in data.get("message", {}).get("items", []):
                    # Prefer PDF link if available
                    pdf_url = None
                    for link in item.get("link", []):
                        if link.get("content-type") == "application/pdf" and link.get("URL"):
                            pdf_url = link["URL"]
                            break

                    # Extract authors
                    authors = []
                    for author in item.get("author", []):
                        given = author.get("given", "")
                        family = author.get("family", "")
                        if given and family:
                            authors.append(f"{given} {family}")
                        elif given:
                            authors.append(given)
                        elif family:
                            authors.append(family)

                    # Extract date
                    date_parts = item.get("issued", {}).get("date-parts", [[None]])[0]
                    year = date_parts[0] if date_parts and date_parts[0] else None

                    papers.append({
                        "id": item.get("DOI", ""),
                        "title": item.get("title", [""])[0] if item.get("title") else "",
                        "authors": authors,
                        "date": str(year) if year else "",
                        "abstract": "",
                        "journal": item.get("container-title", [""])[0] if item.get("container-title") else "",
                        "doi": item.get("DOI", ""),
                        "url": pdf_url or item.get("URL", ""),  # Prefer PDF URL
                        "source": "crossref"
                    })
                return papers

        except httpx.HTTPStatusError as e:
            logger.error(f"Crossref API error: {e.response.status_code}")
            raise SourceError(f"Crossref API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Crossref network error: {e}")
            raise NetworkError(f"Crossref network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Crossref search: {e}")
            raise SourceError(f"Crossref search failed: {e}")

    async def fetch(self, identifier: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        """Fetch a specific paper by DOI."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(
                    f"{self.base_url}/works/{identifier}",
                    headers=headers,
                    timeout=30.0
                )
                # In tests raise_for_status may be a MagicMock; support awaitable
                if hasattr(response, "raise_for_status"):
                    maybe_coro = response.raise_for_status()
                    if hasattr(maybe_coro, "__await__"):
                        await maybe_coro
                data = response.json()

                # Handle both single-item and search-like payloads
                message = data.get("message", {})
                if isinstance(message, dict) and "items" in message:
                    items = message.get("items", []) or [{}]
                    item = items[0] if items else {}
                else:
                    item = message

                # Extract authors
                authors = []
                for author in item.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    if given and family:
                        authors.append(f"{given} {family}")
                    elif given:
                        authors.append(given)
                    elif family:
                        authors.append(family)

                # Extract date
                date_parts = item.get("issued", {}).get("date-parts", [[None]])[0]
                year = date_parts[0] if date_parts and date_parts[0] else None

                # Prefer PDF link if available
                pdf_url = None
                for link in item.get("link", []):
                    if link.get("content-type") == "application/pdf" and link.get("URL"):
                        pdf_url = link["URL"]
                        break

                return {
                    "id": item.get("DOI", ""),
                    "title": item.get("title", [""])[0] if item.get("title") else "",
                    "authors": authors,
                    "date": str(year) if year else "",
                    "abstract": "",
                    "journal": item.get("container-title", [""])[0] if item.get("container-title") else "",
                    "doi": item.get("DOI", ""),
                    "url": pdf_url or item.get("URL", ""),
                    "source": "crossref"
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"Crossref API error: {e.response.status_code}")
            raise SourceError(f"Crossref API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Crossref network error: {e}")
            raise NetworkError(f"Crossref network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Crossref fetch: {e}")
            raise SourceError(f"Crossref fetch failed: {e}")
