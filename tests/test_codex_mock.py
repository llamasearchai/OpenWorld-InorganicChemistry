from __future__ import annotations

import builtins
from openinorganicchemistry.agents.codex import codex_answer


class DummyResp:
    output_text = "mocked codex answer"


class DummyClient:
    class responses:
        @staticmethod
        def create(model: str, input: str):  # type: ignore[override]
            return DummyResp()


def test_codex_mock(monkeypatch):
    # avoid input()
    monkeypatch.setattr(builtins, "input", lambda _: "What is perovskite stability?")
    # inject dummy openai client
    import openinorganicchemistry.agents.codex as mod

    monkeypatch.setattr(mod, "OpenAI", lambda api_key=None: DummyClient())
    # mock web search to return deterministic results
    from openinorganicchemistry.integrations import websearch as ws

    monkeypatch.setattr(ws, "web_search", lambda q, provider=None, max_results=5: [])
    # ensure settings returns a key
    monkeypatch.setenv("OPENAI_API_KEY", "sk-TEST")
    run_id = codex_answer()
    assert isinstance(run_id, str)

