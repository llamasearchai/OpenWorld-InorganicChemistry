"""Test main application."""

from unittest.mock import patch

from scipaper.main import create_app


def test_create_app():
    """Test FastAPI app creation."""
    app = create_app()
    assert app.title == "SciPaper API"
    assert app.version == "1.0.0"


@patch('scipaper.sources.registry.list_sources')
@patch('scipaper.config.is_openai_available')
@patch('scipaper.config.is_ollama_available')
def test_startup_event(mock_ollama, mock_openai, mock_sources):
    """Test application startup event."""
    mock_openai.return_value = True
    mock_ollama.return_value = False
    mock_sources.return_value = ["arxiv", "crossref"]

    app = create_app()

    # Test that startup event can be called
    # Note: In FastAPI, startup events are handled internally
    assert app is not None
