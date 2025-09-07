from __future__ import annotations

from openinorganicchemistry.integrations.websearch import web_search


def test_web_search_duckduckgo(monkeypatch):
    # Force provider to ddg by clearing API keys
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    results = web_search("photovoltaics perovskite stability", provider="duckduckgo", max_results=2)
    assert isinstance(results, list)
    assert len(results) <= 2

