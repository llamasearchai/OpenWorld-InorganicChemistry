from __future__ import annotations

from fastapi.testclient import TestClient
from openinorganicchemistry.api import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_simulation_endpoint():
    client = TestClient(app)
    r = client.post("/simulation", json={"formula": "Ti", "backend": "emt", "supercell": 1})
    assert r.status_code == 200
    data = r.json()
    assert "run_id" in data and isinstance(data["run_id"], str)


