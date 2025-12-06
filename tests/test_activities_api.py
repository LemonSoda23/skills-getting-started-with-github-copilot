import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # make a shallow copy of original participants to restore after each test
    original = {
        name: data["participants"].copy()
        for name, data in activities.items()
    }
    yield
    for name, parts in original.items():
        activities[name]["participants"] = parts


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_cycle():
    email = "pytestuser@example.com"
    activity = "Chess Club"

    # Ensure user is not already signed up
    resp0 = client.get("/activities")
    assert resp0.status_code == 200
    assert email not in resp0.json()[activity]["participants"]

    # Signup
    signup = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup.status_code == 200
    assert "Signed up" in signup.json()["message"]

    # Verify added
    resp1 = client.get("/activities")
    assert email in resp1.json()[activity]["participants"]

    # Unregister
    delete = client.delete(f"/activities/{activity}/participants?email={email}")
    assert delete.status_code == 200
    assert "Unregistered" in delete.json()["message"]

    # Verify removed
    resp2 = client.get("/activities")
    assert email not in resp2.json()[activity]["participants"]


def test_signup_duplicate_fails():
    email = activities["Chess Club"]["participants"][0]
    activity = "Chess Club"
    # Signup with existing email should return 400
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400


def test_unregister_nonexistent_fails():
    email = "not-in-list@example.com"
    activity = "Chess Club"
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 400
