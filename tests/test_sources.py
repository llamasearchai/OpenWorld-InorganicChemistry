"""Test source implementations."""

from scipaper.sources.implementations.crossref import CrossrefSource
from scipaper.sources.registry import get_source, list_sources


def test_list_sources():
    """Test listing available sources."""
    sources = list_sources()
    assert isinstance(sources, list)
    assert len(sources) > 0
    assert "crossref" in sources


def test_get_source():
    """Test getting source instance."""
    source = get_source("crossref")
    assert source is not None
    assert isinstance(source, CrossrefSource)


def test_crossref_init():
    """Test Crossref source initialization."""
    source = CrossrefSource()
    assert source.name == "crossref"
    assert source.base_url == "https://api.crossref.org"
    assert source.user_agent is not None
