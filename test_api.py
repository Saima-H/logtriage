from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze_saves_log():
    r = client.post("/analyze", json={"content": "ERROR test log line"})
    assert r.status_code == 200
    body = r.json()
    assert "id" in body
    assert body["log"] == "ERROR test log line"
    assert body["severity"] in ["info", "warn", "error", "critical", "unknown"]


def test_analyze_rejects_empty_body():
    r = client.post("/analyze", json={})
    assert r.status_code == 422


def test_list_logs_returns_array():
    r = client.get("/logs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_missing_log_returns_404():
    r = client.get("/logs/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Log not found"


def test_get_existing_log():
    created = client.post("/analyze", json={"content": "WARN disk at 90%"}).json()
    log_id = created["id"]
    r = client.get(f"/logs/{log_id}")
    assert r.status_code == 200
    assert r.json()["id"] == log_id
    assert r.json()["content"] == "WARN disk at 90%"