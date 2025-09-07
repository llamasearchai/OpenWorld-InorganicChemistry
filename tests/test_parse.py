from scipaper.utils.parse import parse_text


def test_parse_text_basic():
    text = "See doi:10.1000/xyz123 and arXiv:2103.01234"
    items = parse_text(text)
    types = {i["type"] for i in items}
    assert "doi" in types
    assert "arxiv" in types

