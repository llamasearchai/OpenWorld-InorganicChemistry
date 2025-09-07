from __future__ import annotations

from openinorganicchemistry.integrations.websearch import web_search, WebResult


def test_web_search_duckduckgo(monkeypatch):
    # Mock the DuckDuckGo function to return controlled results
    from openinorganicchemistry.integrations import websearch as ws

    def mock_ddg_search(query: str, max_results: int, timeout: int):
        return [
            WebResult(
                title="Perovskite Solar Cells",
                url="https://example.com/perovskite",
                snippet="Perovskite solar cells show great promise for photovoltaics."
            ),
            WebResult(
                title="Stability Issues in Perovskites",
                url="https://example.com/stability",
                snippet="Research on improving perovskite stability continues."
            )
        ][:max_results]

    monkeypatch.setattr(ws, "_search_duckduckgo", mock_ddg_search)

    # Force provider to ddg by clearing API keys
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    results = web_search("photovoltaics perovskite stability", provider="duckduckgo", max_results=2)
    assert isinstance(results, list)
    assert len(results) <= 2
    if results:
        assert all(isinstance(r, WebResult) for r in results)

