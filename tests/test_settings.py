from __future__ import annotations
from openinorganicchemistry.core.settings import Settings


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-TESTKEY")
    s = Settings.load()
    assert s.openai_api_key and s.openai_api_key.startswith("sk-")


