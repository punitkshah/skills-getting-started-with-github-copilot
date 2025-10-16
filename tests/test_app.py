import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

# Preserve an original deep copy of activities to restore between tests
_original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def restore_data():
    """Automatically restore in-memory activity data before each test.
    Ensures test isolation since endpoints mutate global state.
    """
    # Before test: reset activities to original snapshot
    activities.clear()
    for k, v in _original_activities.items():
        activities[k] = {
            "description": v["description"],
            "schedule": v["schedule"],
            "max_participants": v["max_participants"],
            "participants": list(v["participants"]),
        }
    yield


def test_get_activities_returns_dict():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Spot check a known key
    assert "Chess Club" in data


def test_signup_success():
    email = "newstudent@mergington.edu"
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert "Signed up" in resp.json()["message"]


def test_signup_duplicate_rejected():
    existing = activities["Chess Club"]["participants"][0]
    resp = client.post(f"/activities/Chess%20Club/signup?email={existing}")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student is already signed up"


def test_signup_activity_not_found():
    resp = client.post("/activities/UnknownActivity/signup?email=test@mergington.edu")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    existing = activities["Programming Class"]["participants"][0]
    resp = client.delete(f"/activities/Programming%20Class/participants?email={existing}")
    assert resp.status_code == 200
    assert existing not in activities["Programming Class"]["participants"]
    assert "Removed" in resp.json()["message"]


def test_remove_participant_not_found():
    resp = client.delete("/activities/Programming%20Class/participants?email=absent@mergington.edu")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not found in this activity"
