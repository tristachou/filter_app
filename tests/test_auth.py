
from fastapi.testclient import TestClient

def test_login_for_access_token(test_client: TestClient):
    """Test successful token generation for a valid user."""
    response = test_client.post("/auth/token", data={"username": "user1", "password": "fake_password_1"})
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"

def test_login_invalid_credentials(test_client: TestClient):
    """Test login failure with incorrect password."""
    response = test_client.post("/auth/token", data={"username": "user1", "password": "wrong_password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_read_users_me(test_client: TestClient, auth_token: str):
    """Test the /users/me endpoint to get current user details."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = test_client.get("/auth/users/me", headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["username"] == "user1"
    assert "hashed_password" in json_response # Ensure sensitive data is handled as expected

def test_read_users_me_no_token(test_client: TestClient):
    """Test that /users/me is protected against unauthenticated access."""
    response = test_client.get("/auth/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
