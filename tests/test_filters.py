
from fastapi.testclient import TestClient
import io

def test_upload_filter(test_client: TestClient, auth_token: str):
    """Test successful filter file upload."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    file_content = b"dummy filter content"
    files = {"file": ("test_filter.cube", io.BytesIO(file_content), "application/octet-stream")}
    
    response = test_client.post("/filters/upload", headers=headers, files=files)
    
    assert response.status_code == 201
    json_response = response.json()
    assert json_response["filter_name"] == "test_filter"
    assert json_response["storage_path"].endswith(".cube")

def test_upload_filter_invalid_extension(test_client: TestClient, auth_token: str):
    """Test that uploading a file with an invalid extension is rejected."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    files = {"file": ("invalid.txt", io.BytesIO(b"content"), "text/plain")}
    
    response = test_client.post("/filters/upload", headers=headers, files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_list_user_filters(test_client: TestClient, auth_token: str):
    """Test listing filters for the authenticated user."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Ensure a filter is uploaded first
    files = {"file": ("list_test.cube", io.BytesIO(b"filter"), "application/octet-stream")}
    test_client.post("/filters/upload", headers=headers, files=files)

    # List the filters
    response = test_client.get("/filters/", headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert isinstance(json_response, list)
    assert len(json_response) > 0
