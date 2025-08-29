import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from scipaper.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


def test_system_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@patch("scipaper.sources.arxiv.ArxivSource.search", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_search_endpoint(mock_search):
    mock_search.return_value = [
        {
            "id": "2501.00001",
            "title": "Test Title",
            "authors": ["A", "B"],
            "date": "2025-01-01",
            "source": "arxiv",
            "url": "https://arxiv.org/pdf/2501.00001.pdf",
        }
    ]
    with TestClient(app) as client:
        r = client.post("/api/v1/search", json={"query": "test", "sources": ["arxiv"], "limit": 1})
        assert r.status_code == 200
        data = r.json()["papers"]
        assert len(data) == 1
        assert data[0]["id"] == "2501.00001"


def test_parse_endpoint_text(client):
    r = client.post("/api/v1/parse", json={"text": "doi 10.1/abc", "types": ["doi"], "format": "jsonl"})
    assert r.status_code == 200
    body = r.json()
    assert body["matches"] and body["formatted"].strip().startswith("{")


@patch("scipaper.core.fetcher.Fetcher.fetch", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_fetch_endpoint(mock_fetch, tmp_path: Path):
    fake_path = tmp_path / "paper.pdf"
    fake_path.write_text("dummy")
    mock_fetch.return_value = fake_path
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/fetch",
            json={"identifier": "2501.00001", "output_dir": str(tmp_path), "rename": True},
        )
        assert r.status_code == 200
        assert Path(r.json()["download_path"]).name == "paper.pdf"


@patch("scipaper.agents.paper_agents.AGENTS_AVAILABLE", True)
@patch("scipaper.agents.paper_agents.Runner.run", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_agents_run_endpoint(mock_run):
    class _Res:
        final_output = "Agent OK"

    mock_run.return_value = _Res()
    with patch.dict("os.environ", {"OPENAI_API_KEY": "k"}, clear=False):
        with TestClient(app) as client:
            r = client.post("/api/v1/agents/run", json={"prompt": "test"})
            assert r.status_code == 200
            assert r.json()["final"] == "Agent OK"
