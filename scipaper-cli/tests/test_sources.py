import pytest
from unittest.mock import AsyncMock, patch

from scipaper.sources.crossref import CrossrefSource
from scipaper.sources.semanticscholar import SemanticScholarSource
from scipaper.sources.pubmed import PubMedSource


@pytest.mark.asyncio
async def test_crossref_search_parsing():
    fake = {
        "message": {
            "items": [
                {
                    "title": ["A"],
                    "author": [{"given": "John", "family": "Doe"}],
                    "DOI": "10.1/xyz",
                    "URL": "https://dx.doi.org/10.1/xyz",
                    "issued": {"date-parts": [[2020, 1, 2]]},
                    "link": [{"content-type": "application/pdf", "URL": "https://example.com/a.pdf"}],
                }
            ]
        }
    }
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = fake
        mock_get.return_value.raise_for_status.return_value = None
        src = CrossrefSource()
        res = await src.search("q", 1)
        assert res and res[0]["doi"] == "10.1/xyz" and res[0]["url"].endswith(".pdf")


@pytest.mark.asyncio
async def test_semanticscholar_search_parsing():
    fake = {
        "data": [
            {
                "title": "B",
                "authors": [{"name": "A1"}],
                "year": 2019,
                "externalIds": {"DOI": "10.2/abc"},
                "url": "https://semanticscholar.org/paper/1",
                "openAccessPdf": {"url": "https://example.com/b.pdf"},
            }
        ]
    }
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = fake
        mock_get.return_value.raise_for_status.return_value = None
        src = SemanticScholarSource()
        res = await src.search("q", 1)
        assert res and res[0]["doi"] == "10.2/abc" and res[0]["url"].endswith(".pdf")


@pytest.mark.asyncio
async def test_pubmed_search_parsing():
    fake_search = {"esearchresult": {"idlist": ["12345"]}}
    fake_summary = {"result": {"uids": ["12345"], "12345": {"title": "T", "authors": [{"name": "A"}], "pubdate": "2018", "elocationid": "10.3/def"}}}
    async def side_effect(url, params=None):
        class _R:
            def __init__(self, payload):
                self._p = payload
            def json(self):
                return self._p
            def raise_for_status(self):
                return None
        if "esearch.fcgi" in url:
            return _R(fake_search)
        return _R(fake_summary)

    with patch("httpx.AsyncClient.get", side_effect=side_effect):
        src = PubMedSource()
        res = await src.search("q", 1)
        assert res and res[0]["id"] == "12345" and res[0]["doi"] == "10.3/def"


