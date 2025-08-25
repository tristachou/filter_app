
from fastapi.testclient import TestClient
import io

def test_upload_media(test_client: TestClient, auth_token: str):
    """Test successful media file upload."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Create a dummy file in memory
    file_content = b"dummy media content"
    files = {"file": ("test_media.mp4", io.BytesIO(file_content), "video/mp4")}
    
    response = test_client.post("/media/upload", headers=headers, files=files)
    
    assert response.status_code == 201
    json_response = response.json()
    assert json_response["original_filename"] == "test_media.mp4"
    assert "storage_path" in json_response

def test_upload_media_no_auth(test_client: TestClient):
    """Test that media upload is protected."""
    file_content = b"dummy media content"
    files = {"file": ("test_media.mp4", io.BytesIO(file_content), "video/mp4")}
    
    response = test_client.post("/media/upload", files=files)
    assert response.status_code == 401

def test_list_user_media(test_client: TestClient, auth_token: str):
    """Test listing media for the authenticated user."""
    # First, upload a file to ensure there is data to list
    headers = {"Authorization": f"Bearer {auth_token}"}
    file_content = b"another dummy file"
    files = {"file": ("list_test.mp4", io.BytesIO(file_content), "video/mp4")}
    test_client.post("/media/upload", headers=headers, files=files)

    # Now, list the media
    response = test_client.get("/media/", headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert isinstance(json_response, list)
    assert len(json_response) > 0
    assert json_response[0]["original_filename"] is not None
