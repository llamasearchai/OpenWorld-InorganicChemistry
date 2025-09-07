"""Integration tests for the SciPaper system."""
import pytest
from unittest.mock import AsyncMock, patch
import asyncio

from scipaper.core.fetcher import Fetcher
from scipaper.agents.paper_agents import PaperAgent
from scipaper.sources.registry import get_source


@pytest.mark.asyncio
async def test_fetcher_search_with_cache():
    """Test fetcher search with caching."""
    fetcher = Fetcher()
    query = "test query"
    with patch('scipaper.core.fetcher.aioredis') as mock_redis:
        mock_redis.from_url.return_value = AsyncMock()
        mock_redis_instance = AsyncMock()
        mock_redis_instance.get.return_value = None
        mock_redis_instance.set.return_value = None
        mock_redis.return_value = mock_redis_instance

        # Mock source search
        with patch('scipaper.core.fetcher.get_source') as mock_get_source:
            mock_source = AsyncMock()
            mock_source.search.return_value = [{"title": "Test Paper"}]
            mock_get_source.return_value = mock_source

            results = await fetcher.search(query)
            assert len(results) == 1

            # Check cache set was called
            mock_redis_instance.set.assert_called_once()


@pytest.mark.asyncio
async def test_agent_search_and_analyze():
    """Test agent search and analyze integration."""
    agent = PaperAgent()
    query = "test query"
    with patch('scipaper.agents.paper_agents.Fetcher') as mock_fetcher:
        mock_fetcher_instance = AsyncMock()
        mock_fetcher_instance.search.return_value = [{"title": "Test Paper"}]
        mock_fetcher.return_value = mock_fetcher_instance

        with patch('scipaper.agents.paper_agents.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.choices[0].message.content = "Test analysis"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            result = await agent.search_and_analyze(query)
            assert len(result["papers"]) == 1
            assert "Test analysis" in result["analysis"]


@pytest.mark.asyncio
async def test_source_fetch_async():
    """Test async fetch from source."""
    source = get_source("arxiv")
    identifier = "1234.56789"
    with patch('scipaper.sources.implementations.arxiv.arxiv') as mock_arxiv:
        mock_search = Mock()
        mock_result = Mock()
        mock_search.results.return_value = [mock_result]
        mock_arxiv.Search.return_value = mock_search

        result = await source.fetch(identifier)
        assert result is not None