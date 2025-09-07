"""Test AI agents."""
import pytest
from unittest.mock import Mock, patch
import asyncio

from scipaper.agents.paper_agents import PaperAgent
from scipaper.exceptions import AgentError


@pytest.mark.asyncio
async def test_paper_agent_init():
    """Test PaperAgent initialization."""
    agent = PaperAgent()
    assert hasattr(agent, 'openai_available')
    assert hasattr(agent, 'ollama_available')


@pytest.mark.asyncio
async def test_analyze_papers_openai():
    """Test analyze_papers with OpenAI."""
    agent = PaperAgent()
    papers = [{"title": "Test Paper", "authors": ["Author"], "date": "2023"}]
    with patch('scipaper.agents.paper_agents.is_openai_available', return_value=True):
        with patch('scipaper.agents.paper_agents.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices[0].message.content = "Test analysis"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            analysis = await agent.analyze_papers(papers, "summary")
            assert "Test analysis" in analysis


@pytest.mark.asyncio
async def test_analyze_papers_ollama():
    """Test analyze_papers with Ollama."""
    agent = PaperAgent()
    papers = [{"title": "Test Paper", "authors": ["Author"], "date": "2023"}]
    with patch('scipaper.agents.paper_agents.is_ollama_available', return_value=True):
        with patch('scipaper.agents.paper_agents.OllamaModel') as mock_ollama:
            mock_model = Mock()
            mock_model.generate.return_value = "Test analysis"
            mock_ollama.return_value = mock_model
            analysis = await agent.analyze_papers(papers, "summary")
            assert "Test analysis" in analysis


@pytest.mark.asyncio
async def test_validate_analysis():
    """Test _validate_analysis method."""
    agent = PaperAgent()
    # Test valid analysis
    valid_analysis = "This is a summary of the papers."
    assert agent._validate_analysis(valid_analysis, "summary")
    # Test invalid analysis
    invalid_analysis = "Short"
    assert not agent._validate_analysis(invalid_analysis, "summary")
    # Test with different analysis_type
    comprehensive = "Detailed analysis with insights."
    assert agent._validate_analysis(comprehensive, "comprehensive_analysis")