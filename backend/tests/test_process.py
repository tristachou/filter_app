
from fastapi.testclient import TestClient
import io

def test_apply_filter_to_media(test_client: TestClient, auth_token: str):
    """Test the processing endpoint which simulates a long-running task."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Upload media to get a media_id
    media_files = {"file": ("media.mp4", io.BytesIO(b"media"), "video/mp4")}
    media_response = test_client.post("/media/upload", headers=headers, files=media_files)
    assert media_response.status_code == 201
    media_id = media_response.json()["id"]

    # 2. Upload a filter to get a filter_id
    filter_files = {"file": ("filter.cube", io.BytesIO(b"filter"), "application/octet-stream")}
    filter_response = test_client.post("/filters/upload", headers=headers, files=filter_files)
    assert filter_response.status_code == 201
    filter_id = filter_response.json()["id"]

    # 3. Call the process endpoint
    process_payload = {"media_id": media_id, "filter_id": filter_id}
    response = test_client.post("/process/", headers=headers, json=process_payload)

    assert response.status_code == 200
    json_response = response.json()
    assert "message" in json_response
    assert "output_path" in json_response
    assert json_response["output_path"].startswith("storage/processed_output/")

def test_process_invalid_media_id(test_client: TestClient, auth_token: str):
    """Test the process endpoint with a non-existent media ID."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Upload a filter to get a valid filter_id
    filter_files = {"file": ("filter.cube", io.BytesIO(b"filter"), "application/octet-stream")}
    filter_response = test_client.post("/filters/upload", headers=headers, files=filter_files)
    filter_id = filter_response.json()["id"]

    invalid_media_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    process_payload = {"media_id": invalid_media_id, "filter_id": filter_id}
    response = test_client.post("/process/", headers=headers, json=process_payload)

    assert response.status_code == 404
    assert "Media item not found" in response.json()["detail"]
