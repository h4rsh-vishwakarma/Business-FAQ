from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

TEST_DB = ROOT_DIR / f"test_chatbot_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.resolve()}"

from app.main import create_app  # noqa: E402


def teardown_module() -> None:
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass


client = TestClient(create_app())


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_faq_response() -> None:
    response = client.post("/chat", json={"session_id": "session-faq", "message": "What are your hours?"})
    assert response.status_code == 200
    payload = response.json()
    assert "open" in payload["message"].lower()
    assert payload["lead_captured"] is False


def test_lead_capture_flow() -> None:
    session_id = "session-lead"

    first = client.post("/chat", json={"session_id": session_id, "message": "I want to book a table"})
    assert first.status_code == 200
    assert "name" in first.json()["message"].lower()

    second = client.post("/chat", json={"session_id": session_id, "message": "Aarav"})
    assert second.status_code == 200
    assert "phone number or email" in second.json()["message"].lower()

    third = client.post("/chat", json={"session_id": session_id, "message": "aarav@example.com"})
    assert third.status_code == 200
    assert third.json()["lead_captured"] is True

    leads = client.get("/api/leads", auth=("admin", "admin123"))
    assert leads.status_code == 200
    data = leads.json()
    assert any(lead["name"] == "Aarav" for lead in data)
