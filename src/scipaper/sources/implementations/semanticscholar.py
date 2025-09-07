"""Semantic Scholar data source implementation."""

from typing import Any, Optional
from urllib.parse import urlencode

import httpx
from loguru import logger

from ...config import settings
from ...exceptions import NetworkError, SourceError
from ..base_source import BaseSource


class SemanticScholarSource(BaseSource):
    """Semantic Scholar data source for academic papers with rich metadata."""

    name = "semanticscholar"
    base_url = "https://api.semanticscholar.org"

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'semanticscholar_api_key', None)
        self.headers = {"User-Agent": "SciPaper/1.0"}
        if self.api_key:
            self.headers["x-api-key"] = self.api_key

    async def search(self, query: str, limit: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        """Search for papers using Semantic Scholar API."""
        try:
            # Use the graph API for search
            search_url = f"{self.base_url}/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": min(limit, 100),  # Semantic Scholar max is 100
                "fields": "paperId,title,authors,year,venue,abstract,citationCount,influentialCitationCount,openAccessPdf"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    search_url,
                    params=params,
                    headers=self.headers,
                    timeout=30.0
                )
                # Support awaitable MagicMock in tests
                maybe_coro = response.raise_for_status()
                if hasattr(maybe_coro, "__await__"):
                    await maybe_coro
                data = response.json()

            papers = []
            for paper in data.get("data", []):
                paper_data = self._extract_paper_data(paper)
                if paper_data:
                    papers.append(paper_data)

            return papers[:limit]

        except httpx.HTTPStatusError as e:
            logger.error(f"Semantic Scholar API error: {e.response.status_code}")
            raise SourceError(f"Semantic Scholar API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Semantic Scholar network error: {e}")
            raise NetworkError(f"Semantic Scholar network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Semantic Scholar search: {e}")
            raise SourceError(f"Semantic Scholar search failed: {e}")

    async def fetch(self, identifier: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        """Fetch a specific paper by its Semantic Scholar paper ID."""
        try:
            # Clean the identifier
            paper_id = identifier.replace("SemanticScholar:", "").strip()

            # Use the graph API to get detailed paper information
            fetch_url = f"{self.base_url}/graph/v1/paper/{paper_id}"
            params = {
                "fields": "paperId,externalIds,title,authors,year,venue,abstract,citationCount,influentialCitationCount,openAccessPdf,references,citations"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    fetch_url,
                    params=params,
                    headers=self.headers,
                    timeout=30.0
                )
                maybe_coro = response.raise_for_status()
                if hasattr(maybe_coro, "__await__"):
                    await maybe_coro
                paper = response.json()

            return self._extract_detailed_paper_data(paper)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Paper not found: {identifier}")
                return None
            logger.error(f"Semantic Scholar API error: {e.response.status_code}")
            raise SourceError(f"Semantic Scholar API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Semantic Scholar network error: {e}")
            raise NetworkError(f"Semantic Scholar network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Semantic Scholar fetch: {e}")
            raise SourceError(f"Semantic Scholar fetch failed: {e}")

    def _extract_paper_data(self, paper: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Extract paper data from Semantic Scholar search result."""
        try:
            # Extract authors
            authors = []
            for author in paper.get("authors", []):
                if isinstance(author, dict):
                    name = author.get("name", "")
                    if name:
                        authors.append(name)

            # Extract DOI from external IDs if available
            doi = ""
            external_ids = paper.get("externalIds", {})
            if external_ids:
                doi = external_ids.get("DOI", "")

            # Get PDF URL
            pdf_url = ""
            open_access_pdf = paper.get("openAccessPdf")
            if open_access_pdf and isinstance(open_access_pdf, dict):
                pdf_url = open_access_pdf.get("url", "")

            # Include external_ids for tests
            return {
                "id": f"SemanticScholar:{paper.get('paperId', '')}",
                "title": paper.get("title", ""),
                "authors": authors,
                "date": str(paper.get("year", "")),
                "abstract": paper.get("abstract", ""),
                "journal": paper.get("venue", ""),
                "doi": doi,
                "url": pdf_url or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                "source": "semanticscholar",
                "citation_count": paper.get("citationCount", 0),
                "influential_citation_count": paper.get("influentialCitationCount", 0),
                "external_ids": paper.get("externalIds", {}),
            }

        except Exception as e:
            logger.error(f"Error extracting paper data: {e}")
            return None

    def _extract_detailed_paper_data(self, paper: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Extract detailed paper data from Semantic Scholar detailed result."""
        try:
            base_data = self._extract_paper_data(paper)
            if not base_data:
                return None

            # Add additional detailed information
            base_data.update({
                "references_count": len(paper.get("references", [])),
                "citations_count": len(paper.get("citations", [])),
                "semantic_scholar_id": paper.get("paperId", ""),
                "external_ids": paper.get("externalIds", {}),
                "references": [
                    {
                        "id": f"SemanticScholar:{ref.get('paperId', '')}",
                        "title": ref.get("title", ""),
                        "year": ref.get("year")
                    }
                    for ref in paper.get("references", [])[:10]  # Limit to first 10 references
                ],
                "citations": [
                    {
                        "id": f"SemanticScholar:{cit.get('paperId', '')}",
                        "title": cit.get("title", ""),
                        "year": cit.get("year")
                    }
                    for cit in paper.get("citations", [])[:10]  # Limit to first 10 citations
                ]
            })

            return base_data

        except Exception as e:
            logger.error(f"Error extracting detailed paper data: {e}")
            return None
