from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_remove_participant_success():
    # Ensure a known participant exists
    activity = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity]["participants"]

    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "Removed" in data["message"]
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    activity = "Chess Club"
    missing_email = "doesnotexist@mergington.edu"
    assert missing_email not in activities[activity]["participants"]

    resp = client.delete(f"/activities/{activity}/participants", params={"email": missing_email})
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Participant not found in this activity"
