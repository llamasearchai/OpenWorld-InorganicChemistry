import pytest
from scipaper.utils import parse as p


def test_parse_ids_from_text_basic():
    s = "DOI 10.1109/83.544569 and arXiv:2407.13619 plus https://example.com/a.pdf"
    items = p.parse_ids_from_text(s, ["doi", "arxiv", "url"])
    values = {i["id"] for i in items}
    assert "10.1109/83.544569" in values
    assert "arXiv:2407.13619" in values
    assert "https://example.com/a.pdf" in values


def test_format_output():
    items = [{"id": "10.1/abc", "type": "doi"}]
    assert p.format_output(items, "raw").strip() == "10.1/abc"
    assert "\n" not in p.format_output(items, "jsonl")
    assert p.format_output(items, "csv").strip() == "10.1/abc,doi"


def test_find_pdf_url_from_html():
    html = '<html><body><embed id="pdf" type="application/pdf" src="/paper.pdf"></body></html>'
    assert p.find_pdf_url(html) == "/paper.pdf"


