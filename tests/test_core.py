"""Test core modules."""

from scipaper.core.fetcher import Fetcher


def test_fetcher_init():
    """Test Fetcher initialization."""
    fetcher = Fetcher()
    assert hasattr(fetcher, 'available_sources')
    assert len(fetcher.available_sources) > 0


def test_fetcher_methods():
    """Test basic fetcher methods without API calls."""
    fetcher = Fetcher()

    # Test basic properties
    assert hasattr(fetcher, 'available_sources')
    assert len(fetcher.available_sources) > 0

    # Test helper methods
    sources = fetcher.get_available_sources()
    assert isinstance(sources, list)
    assert len(sources) > 0

    assert fetcher.is_source_available("crossref")
    assert not fetcher.is_source_available("nonexistent")


def test_fetcher_available_sources():
    """Test getting available sources."""
    fetcher = Fetcher()
    sources = fetcher.get_available_sources()
    assert isinstance(sources, list)
    assert len(sources) > 0


def test_fetcher_is_source_available():
    """Test checking if source is available."""
    fetcher = Fetcher()
    assert fetcher.is_source_available("crossref")
    assert not fetcher.is_source_available("nonexistent")
