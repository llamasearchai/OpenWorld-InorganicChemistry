from __future__ import annotations

import builtins
from openinorganicchemistry.agents.literature import literature_query


class DummyResp:
    output_text = "mocked output"


class DummyClient:
    class responses:
        @staticmethod
        def create(model: str, input: str):  # type: ignore[override]
            return DummyResp()


def test_literature_mock(monkeypatch):
    # avoid input() in tests
    monkeypatch.setattr(builtins, "input", lambda _: "perovskite stability")
    # inject dummy client
    import openinorganicchemistry.agents.literature as mod

    monkeypatch.setattr(mod, "OpenAI", lambda api_key=None: DummyClient())
    # ensure settings returns a key
    from openinorganicchemistry.core.settings import Settings

    monkeypatch.setenv("OPENAI_API_KEY", "sk-TEST")
    run_id = literature_query()
    assert isinstance(run_id, str)


