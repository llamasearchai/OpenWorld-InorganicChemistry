"""Test utils modules."""

from scipaper.utils.ids import classify_identifier, extract_identifiers
from scipaper.utils.parse import parse_text


def test_classify_identifier():
    """Test identifier classification."""
    assert classify_identifier("10.1000/xyz123") == "doi"
    assert classify_identifier("arXiv:2103.01234") == "arxiv"
    assert classify_identifier("978-0123456789") == "isbn"
    assert classify_identifier("https://example.com") == "url"
    assert classify_identifier("invalid") == "unknown"


def test_extract_identifiers():
    """Test identifier extraction from text."""
    text = "Check doi:10.1000/xyz123 and arXiv:2103.01234"
    results = extract_identifiers(text)

    assert len(results) == 2
    assert results[0]["type"] == "doi"
    assert results[0]["value"] == "10.1000/xyz123"
    assert results[0]["position"] == "10"  # Position of "10.1000/xyz123" in text
    assert results[1]["type"] == "arxiv"
    assert results[1]["value"] == "arXiv:2103.01234"
    assert results[1]["position"] == "29"


def test_extract_identifiers_isbn():
    """Test ISBN extraction."""
    text = "ISBN: 978-0123456789 and 0123456789"
    results = extract_identifiers(text)
    assert len(results) == 1
    assert results[0]["type"] == "isbn"


def test_extract_identifiers_url():
    """Test URL extraction."""
    text = "Visit https://example.com and http://test.org"
    results = extract_identifiers(text)
    assert len(results) == 2
    assert all(r["type"] == "url" for r in results)


def test_extract_identifiers_deduplication():
    """Test deduplication of identical identifiers."""
    text = "doi:10.1000/xyz123 and doi:10.1000/xyz123"
    results = extract_identifiers(text)
    assert len(results) == 1  # Should deduplicate
    assert results[0]["type"] == "doi"
    assert results[0]["value"] == "10.1000/xyz123"


def test_parse_text():
    """Test text parsing for identifiers."""
    text = "See doi:10.1000/xyz123 and arXiv:2103.01234"
    results = parse_text(text)

    assert len(results) == 2
    assert results[0]["type"] == "doi"
    assert results[1]["type"] == "arxiv"


def test_parse_text_with_filter():
    """Test text parsing with type filtering."""
    text = "See doi:10.1000/xyz123 and arXiv:2103.01234"
    results = parse_text(text, types=["doi"])

    assert len(results) == 1
    assert results[0]["type"] == "doi"
