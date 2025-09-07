"""Tests for Semantic Scholar source implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from scipaper.sources.implementations.semanticscholar import SemanticScholarSource


class TestSemanticScholarSource:
    """Test cases for Semantic Scholar source."""

    def setup_method(self):
        """Set up test fixtures."""
        self.source = SemanticScholarSource()

    def test_source_name(self):
        """Test source name property."""
        assert self.source.name == "semanticscholar"

    def test_source_initialization(self):
        """Test source initialization with settings."""
        assert hasattr(self.source, 'api_key')
        assert self.source.base_url == "https://api.semanticscholar.org"
        assert "User-Agent" in self.source.headers

    @patch('httpx.AsyncClient')
    async def test_search_success(self, mock_client):
        """Test successful search operation."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={
            "data": [
                {
                    "paperId": "test123",
                    "title": "Test Paper Title",
                    "authors": [
                        {"name": "John Smith"},
                        {"name": "Jane Doe"}
                    ],
                    "year": 2023,
                    "venue": "Test Journal",
                    "abstract": "Test abstract content",
                    "citationCount": 42,
                    "influentialCitationCount": 10,
                    "openAccessPdf": {
                        "url": "https://example.com/paper.pdf"
                    },
                    "externalIds": {
                        "DOI": "10.1000/test"
                    }
                }
            ]
        })

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        results = await self.source.search("test query", limit=5)

        assert len(results) == 1
        paper = results[0]
        assert paper["id"] == "SemanticScholar:test123"
        assert paper["title"] == "Test Paper Title"
        assert paper["authors"] == ["John Smith", "Jane Doe"]
        assert paper["date"] == "2023"
        assert paper["journal"] == "Test Journal"
        assert paper["abstract"] == "Test abstract content"
        assert paper["doi"] == "10.1000/test"
        assert paper["url"] == "https://example.com/paper.pdf"
        assert paper["citation_count"] == 42
        assert paper["influential_citation_count"] == 10
        assert paper["source"] == "semanticscholar"

    @patch('httpx.AsyncClient')
    async def test_search_no_results(self, mock_client):
        """Test search with no results."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"data": []})

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        results = await self.source.search("nonexistent query", limit=5)

        assert results == []

    @patch('httpx.AsyncClient')
    async def test_search_api_error(self, mock_client):
        """Test search with API error."""
        from httpx import HTTPStatusError
        from scipaper.exceptions import SourceError

        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.raise_for_status = MagicMock(side_effect=HTTPStatusError(
            "Too Many Requests", request=MagicMock(), response=mock_response
        ))

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        with pytest.raises(SourceError, match="Semantic Scholar API error: 429"):
            await self.source.search("test query", limit=5)

    @patch('httpx.AsyncClient')
    async def test_fetch_success(self, mock_client):
        """Test successful fetch operation."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={
            "paperId": "test123",
            "title": "Detailed Test Paper",
            "authors": [{"name": "John Smith"}],
            "year": 2023,
            "venue": "Test Journal",
            "abstract": "Detailed abstract",
            "citationCount": 50,
            "influentialCitationCount": 15,
            "openAccessPdf": {"url": "https://example.com/detailed.pdf"},
            "externalIds": {"DOI": "10.1000/detailed"},
            "references": [
                {"paperId": "ref1", "title": "Reference 1", "year": 2022},
                {"paperId": "ref2", "title": "Reference 2", "year": 2021}
            ],
            "citations": [
                {"paperId": "cit1", "title": "Citation 1", "year": 2024}
            ]
        })

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await self.source.fetch("test123")

        assert result is not None
        assert result["id"] == "SemanticScholar:test123"
        assert result["title"] == "Detailed Test Paper"
        assert result["citation_count"] == 50
        assert result["influential_citation_count"] == 15
        assert result["semantic_scholar_id"] == "test123"
        assert len(result["references"]) == 2
        assert len(result["citations"]) == 1
        assert result["references_count"] == 2
        assert result["citations_count"] == 1

    @patch('httpx.AsyncClient')
    async def test_fetch_with_prefix(self, mock_client):
        """Test fetch with SemanticScholar: prefix."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={
            "paperId": "test123",
            "title": "Test Paper",
            "authors": [{"name": "Test Author"}],
            "year": 2023
        })

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await self.source.fetch("SemanticScholar:test123")

        assert result is not None
        assert result["id"] == "SemanticScholar:test123"

    @patch('httpx.AsyncClient')
    async def test_fetch_not_found(self, mock_client):
        """Test fetch with 404 error."""
        from httpx import HTTPStatusError

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock(side_effect=HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        ))

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await self.source.fetch("nonexistent")

        assert result is None

    def test_extract_paper_data_with_minimal_info(self):
        """Test extracting paper data with minimal information."""
        paper_data = {
            "paperId": "test123",
            "title": "Minimal Paper",
            "authors": [],
            "year": 2023
        }

        result = self.source._extract_paper_data(paper_data)

        assert result is not None
        assert result["id"] == "SemanticScholar:test123"
        assert result["title"] == "Minimal Paper"
        assert result["authors"] == []
        assert result["date"] == "2023"
        assert result["journal"] == ""
        assert result["abstract"] == ""
        assert result["doi"] == ""
        assert result["citation_count"] == 0
        assert result["influential_citation_count"] == 0

    def test_extract_paper_data_with_external_ids(self):
        """Test extracting paper data with external IDs."""
        paper_data = {
            "paperId": "test123",
            "title": "Paper with DOI",
            "authors": [{"name": "Test Author"}],
            "year": 2023,
            "externalIds": {
                "DOI": "10.1000/test",
                "PubMed": "12345"
            }
        }

        result = self.source._extract_paper_data(paper_data)

        assert result is not None
        assert result["doi"] == "10.1000/test"
        assert result["external_ids"]["DOI"] == "10.1000/test"
        assert result["external_ids"]["PubMed"] == "12345"

    def test_extract_paper_data_with_open_access_pdf(self):
        """Test extracting paper data with open access PDF."""
        paper_data = {
            "paperId": "test123",
            "title": "Paper with PDF",
            "authors": [{"name": "Test Author"}],
            "year": 2023,
            "openAccessPdf": {
                "url": "https://example.com/paper.pdf"
            }
        }

        result = self.source._extract_paper_data(paper_data)

        assert result is not None
        assert result["url"] == "https://example.com/paper.pdf"

    def test_extract_paper_data_error_handling(self):
        """Test error handling in paper data extraction."""
        # Test with None
        result = self.source._extract_paper_data(None)
        assert result is None

        # Test with empty dict
        result = self.source._extract_paper_data({})
        assert result is not None
        assert result["id"] == "SemanticScholar:"
        assert result["title"] == ""

    def test_extract_detailed_paper_data_error_handling(self):
        """Test error handling in detailed paper data extraction."""
        # Test with None
        result = self.source._extract_detailed_paper_data(None)
        assert result is None

        # Test with minimal data
        minimal_data = {"paperId": "test123", "title": "Test"}
        result = self.source._extract_detailed_paper_data(minimal_data)
        assert result is not None
        assert result["references_count"] == 0
        assert result["citations_count"] == 0
        assert result["references"] == []
        assert result["citations"] == []
