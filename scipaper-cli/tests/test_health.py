from fastapi.testclient import TestClient
from scipaper.main import app


def test_health():
    c = TestClient(app)
    r = c.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
