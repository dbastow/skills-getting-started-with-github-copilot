import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


client = TestClient(app)


def test_get_activities_returns_seeded_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_student_to_activity():
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")

    assert response.status_code == 200
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    assert response.json() == {"message": "Signed up newstudent@mergington.edu for Chess Club"}


def test_signup_rejects_duplicate_email_for_activity():
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_rejects_unknown_activity():
    response = client.post("/activities/Unknown Activity/signup?email=student@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant_from_activity():
    response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}


def test_unregister_rejects_missing_participant():
    response = client.delete("/activities/Chess Club/signup?email=ghost@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
