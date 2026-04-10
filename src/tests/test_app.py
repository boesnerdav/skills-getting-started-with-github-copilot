import pytest
from fastapi.testclient import TestClient

def test_root_redirect(client: TestClient):
    """Test that root endpoint redirects to static HTML"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers.get("location", "")

def test_get_activities(client: TestClient, mock_activities):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities

    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_for_activity_success(client: TestClient):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]

def test_signup_for_activity_already_signed_up(client: TestClient):
    """Test signup when user is already signed up"""
    # First signup
    client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")

    # Second signup should fail
    response = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()

def test_signup_for_nonexistent_activity(client: TestClient):
    """Test signup for activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()