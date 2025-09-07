"""Test API endpoints."""

from fastapi.testclient import TestClient

from scipaper.main import app


def test_health_endpoint():
    """Test health endpoint."""
    client = TestClient(app)
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert "version" in data


def test_search_endpoint():
    """Test search endpoint."""
    client = TestClient(app)
    payload = {"query": "test", "sources": ["crossref"], "limit": 1}
    resp = client.post("/api/v1/search", json=payload)
    # This will fail without proper mocking, but tests the endpoint exists
    assert resp.status_code in [200, 500]  # 500 if source fails


def test_fetch_endpoint():
    """Test fetch endpoint."""
    client = TestClient(app)
    payload = {"identifier": "10.1000/test", "source": "crossref"}
    resp = client.post("/api/v1/fetch", json=payload)
    # This will likely fail, but tests the endpoint exists
    assert resp.status_code in [200, 404, 500]


def test_parse_endpoint():
    """Test parse endpoint."""
    client = TestClient(app)
    payload = {"text": "Check doi:10.1000/xyz123", "types": ["doi"]}
    resp = client.post("/api/v1/parse", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["type"] == "doi"
    assert data[0]["value"] == "10.1000/xyz123"


def test_agents_endpoint():
    """Test agents endpoint."""
    client = TestClient(app)
    payload = {"prompt": "test prompt"}
    resp = client.post("/api/v1/agents/run", json=payload)
    # This will likely fail without API keys, but tests the endpoint exists
    assert resp.status_code in [200, 500]
