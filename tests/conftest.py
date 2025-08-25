
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def test_client():
    """Create a TestClient instance for the FastAPI app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def auth_token(test_client):
    """Authenticate and get a JWT token for user1."""
    response = test_client.post("/auth/token", data={"username": "user1", "password": "fake_password_1"})
    assert response.status_code == 200
    return response.json()["access_token"]
