import pytest
import httpx
from unittest.mock import AsyncMock, patch
from scipaper.agents.paper_agents import run_agent, OllamaModel

@pytest.fixture
def mock_http():
    return httpx.AsyncClient()

@pytest.mark.asyncio
async def test_ollama_model_generate(mock_http):
    """Test Ollama model generates responses (sync client)."""
    model = OllamaModel()
    with patch('ollama.Client.generate') as mock_gen:
        mock_gen.return_value = {'response': 'Test response'}
        result = await model.generate("test prompt", {"http": mock_http})
        assert result == "Test response"

@pytest.mark.asyncio
async def test_ollama_tool_use(mock_http):
    """Test Ollama model handles tool use"""
    model = OllamaModel()
    with patch('ollama.Client.generate') as mock_gen:
        mock_gen.return_value = {'response': 'use tool_search'}
        with patch('scipaper.agents.tools.tool_search', new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = "Search results"
            # Force routing via explicit prefix to avoid live arxiv call
            result = await model.generate("search machine learning", {"http": mock_http})
            assert result == "Search results"

@pytest.mark.asyncio
async def test_run_agent_with_ollama(mock_http):
    """Test agent runner falls back to Ollama"""
    with patch('scipaper.agents.paper_agents.AGENTS_AVAILABLE', False):
        with patch('scipaper.agents.paper_agents.OllamaModel.generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Ollama response"
            result = await run_agent("test prompt", mock_http)
            assert result == "Ollama response"

@pytest.mark.asyncio
async def test_run_agent_with_openai(mock_http):
    """Test agent runner uses OpenAI when available"""
    with patch('scipaper.agents.paper_agents.AGENTS_AVAILABLE', True):
        with patch.dict('os.environ', {"OPENAI_API_KEY": "fake_key"}):
            # Patch the imported Runner symbol inside module namespace
            from scipaper.agents import paper_agents as pa
            with patch.object(pa.Runner, 'run', new_callable=AsyncMock) as mock_run:
                mock_run.return_value.final_output = "OpenAI response"
                result = await run_agent("test prompt", mock_http)
                assert result == "OpenAI response"

@pytest.mark.asyncio
async def test_run_agent_fallback_to_ollama(mock_http):
    """Test agent falls back to Ollama when OpenAI key missing"""
    with patch('scipaper.agents.paper_agents.AGENTS_AVAILABLE', True):
        with patch('os.getenv', return_value=None):
            with patch('scipaper.agents.paper_agents.OllamaModel.generate', new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = "Fallback response"
                result = await run_agent("test prompt", mock_http)
                assert result == "Fallback response"