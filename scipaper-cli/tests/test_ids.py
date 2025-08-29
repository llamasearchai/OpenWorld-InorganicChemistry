from scipaper.utils.ids import classify_identifier


def test_id_classification():
    assert classify_identifier("2401.12345") == "arxiv"
    assert classify_identifier("cs/0112017") == "arxiv"
    assert classify_identifier("10.1145/12345.67890") == "doi"
    assert classify_identifier("https://example.com/a.pdf") == "url"
    assert classify_identifier("weird") == "unknown"
