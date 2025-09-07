"""Tests for PubMed source implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from scipaper.sources.implementations.pubmed import PubMedSource


class TestPubMedSource:
    """Test cases for PubMed source."""

    def setup_method(self):
        """Set up test fixtures."""
        self.source = PubMedSource()

    def test_source_name(self):
        """Test source name property."""
        assert self.source.name == "pubmed"

    def test_source_initialization(self):
        """Test source initialization with settings."""
        assert hasattr(self.source, 'email')
        assert hasattr(self.source, 'api_key')
        assert self.source.base_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    @patch('httpx.AsyncClient')
    async def test_search_success(self, mock_client):
        """Test successful search operation."""
        # Mock the HTTP responses
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={
            "esearchresult": {
                "idlist": ["12345", "67890"]
            }
        })

        mock_fetch_response = AsyncMock()
        mock_fetch_response.raise_for_status = MagicMock()
        mock_fetch_response.text = """<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>12345</PMID>
                    <Article>
                        <Journal>
                            <Title>Test Journal</Title>
                        </Journal>
                        <ArticleTitle>Test Paper Title</ArticleTitle>
                        <Abstract>
                            <AbstractText>Test abstract</AbstractText>
                        </Abstract>
                        <AuthorList>
                            <Author>
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                        </AuthorList>
                        <PubDate>
                            <Year>2023</Year>
                        </PubDate>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>"""

        mock_client.return_value.__aenter__.return_value.get.side_effect = [
            mock_response, mock_fetch_response
        ]

        results = await self.source.search("test query", limit=5)

        assert len(results) == 1
        assert results[0]["id"] == "PMID:12345"
        assert results[0]["title"] == "Test Paper Title"
        assert results[0]["authors"] == ["John Smith"]
        assert results[0]["date"] == "2023"
        assert results[0]["journal"] == "Test Journal"
        assert results[0]["source"] == "pubmed"

    @patch('httpx.AsyncClient')
    async def test_search_no_results(self, mock_client):
        """Test search with no results."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={
            "esearchresult": {
                "idlist": []
            }
        })

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        results = await self.source.search("nonexistent query", limit=5)

        assert results == []

    @patch('httpx.AsyncClient')
    async def test_search_api_error(self, mock_client):
        """Test search with API error."""
        from httpx import HTTPStatusError
        from scipaper.exceptions import SourceError

        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.raise_for_status = MagicMock(side_effect=HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        ))

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        with pytest.raises(SourceError, match="PubMed API error: 500"):
            await self.source.search("test query", limit=5)

    @patch('httpx.AsyncClient')
    async def test_fetch_success(self, mock_client):
        """Test successful fetch operation."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = """<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>12345</PMID>
                    <Article>
                        <Journal>
                            <Title>Test Journal</Title>
                        </Journal>
                        <ArticleTitle>Test Paper Title</ArticleTitle>
                        <Abstract>
                            <AbstractText>Test abstract</AbstractText>
                        </Abstract>
                        <AuthorList>
                            <Author>
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                        </AuthorList>
                        <PubDate>
                            <Year>2023</Year>
                        </PubDate>
                        <ELocationID EIdType="doi">10.1000/test</ELocationID>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>"""

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await self.source.fetch("12345")

        assert result is not None
        assert result["id"] == "PMID:12345"
        assert result["title"] == "Test Paper Title"
        assert result["doi"] == "10.1000/test"
        assert result["url"] == "https://pubmed.ncbi.nlm.nih.gov/12345/"

    @patch('httpx.AsyncClient')
    async def test_fetch_with_pmid_prefix(self, mock_client):
        """Test fetch with PMID: prefix."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = """<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>12345</PMID>
                    <Article>
                        <ArticleTitle>Test Paper</ArticleTitle>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>"""

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await self.source.fetch("PMID:12345")

        assert result is not None
        assert result["id"] == "PMID:12345"

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

    def test_parse_pubmed_xml_malformed(self):
        """Test parsing malformed XML."""
        malformed_xml = "<invalid>xml<content>"
        results = self.source._parse_pubmed_xml(malformed_xml, ["12345"])
        assert results == []

    def test_extract_paper_data_error_handling(self):
        """Test error handling in paper data extraction."""
        # Test with None article element
        result = self.source._extract_paper_data(None)
        assert result is None

        # Test with empty article element
        result = self.source._extract_paper_data({})
        assert result is not None
        assert result["id"] == "PMID:"
        assert result["title"] == ""
