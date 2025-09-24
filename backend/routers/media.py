from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from typing import List, Dict
import uuid
from pathlib import Path

from models.schemas import MediaItemInDB
from routers.auth import get_current_user
# Import the new DynamoDB-based functions
from utils.database import add_media_item, get_user_media, get_media_by_id, delete_user_media
from utils.s3_client import upload_file_to_s3, create_presigned_url, delete_file_from_s3

# --- Router --- #
router = APIRouter(
    prefix="/media",
    tags=["Media Management"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/upload", response_model=MediaItemInDB, status_code=status.HTTP_201_CREATED)
async def upload_media(user_claims: Dict = Depends(get_current_user), file: UploadFile = File(...)):
    """
    Handles the upload of a media file (photo or video) to S3 and saves metadata to DynamoDB.
    """
    user_id = user_claims.get("sub")
    file_extension = Path(file.filename).suffix
    
    object_key = f"uploads/{user_id}/{uuid.uuid4()}{file_extension}"

    # Upload file to S3
    upload_file_to_s3(file.file, object_key, file.content_type)

    # Create metadata record
    media_item = MediaItemInDB(
        owner_id=user_id,
        original_filename=file.filename,
        storage_path=object_key,
        media_type=file.content_type,
    )

    # Add the new media item to DynamoDB
    add_media_item(media_item.model_dump())

    return media_item

@router.get("/", response_model=List[MediaItemInDB])
async def list_user_media(user_claims: Dict = Depends(get_current_user)):
    """
    Retrieves a list of all media items uploaded by the current user from DynamoDB.
    """
    user_id = user_claims.get("sub")
    media_items_data = get_user_media(user_id)
    return [MediaItemInDB(**item) for item in media_items_data]

@router.delete("/all", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_user_media(user_claims: Dict = Depends(get_current_user)):
    """
    Deletes all media items for the current user from DynamoDB and S3.
    """
    user_id = user_claims.get("sub")
    
    # This function now gets paths from DynamoDB and deletes the DB entries
    object_keys_to_delete = delete_user_media(user_id)
    
    # Delete corresponding files from S3
    for object_key in object_keys_to_delete:
        try:
            delete_file_from_s3(object_key)
        except HTTPException as e:
            print(f"Error deleting S3 object {object_key}: {e.detail}")
            # Continue with other deletions even if one fails
            
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/download/{media_id}")
async def download_media_file(media_id: uuid.UUID, user_claims: Dict = Depends(get_current_user)):
    """
    Generates a pre-signed URL for downloading a media file from S3.
    """
    user_id = user_claims.get("sub")
    media_item = get_media_by_id(media_id)

    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found.")

    if media_item["owner_id"] != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to download this file.")

    s3_object_key = media_item["storage_path"]
    presigned_url = create_presigned_url(s3_object_key)

    if not presigned_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate download URL.")

    return RedirectResponse(url=presigned_url)

@router.get("/{media_id}", response_model=MediaItemInDB)
async def get_single_media(media_id: uuid.UUID, user_claims: Dict = Depends(get_current_user)):
    """
    Retrieves a single media item by its ID from DynamoDB.
    """
    user_id = user_claims.get("sub")
    media_item_data = get_media_by_id(media_id)

    if not media_item_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    if media_item_data["owner_id"] != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this media")

    return MediaItemInDB(**media_item_data)