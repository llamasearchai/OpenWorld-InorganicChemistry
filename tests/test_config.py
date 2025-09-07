"""Test configuration module."""

from scipaper.config import get_setting, is_ollama_available, is_openai_available, settings


def test_settings():
    """Test settings object creation."""
    assert hasattr(settings, 'fastapi_host')
    assert hasattr(settings, 'fastapi_port')
    assert hasattr(settings, 'openai_api_key')
    assert hasattr(settings, 'ollama_host')
    assert hasattr(settings, 'ollama_port')
    assert hasattr(settings, 'downloads_dir')


def test_get_setting():
    """Test get_setting function."""
    assert get_setting('fastapi_host') is not None
    assert get_setting('nonexistent', 'default') == 'default'


def test_openai_availability():
    """Test OpenAI availability check."""
    result = is_openai_available()
    assert isinstance(result, bool)


def test_ollama_availability():
    """Test Ollama availability check."""
    result = is_ollama_available()
    assert isinstance(result, bool)
