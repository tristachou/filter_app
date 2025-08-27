from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Response
from fastapi.responses import FileResponse
from typing import List, Annotated
import uuid
from pathlib import Path
import os

from models.schemas import MediaItemInDB, User
from routers.auth import get_current_user
from utils.database import load_db, save_db, add_media_item, get_user_media, get_media_by_id, delete_user_media, ROOT_DIR

# --- Router --- #
router = APIRouter(
    prefix="/media",
    tags=["Media Management"],
    dependencies=[Depends(get_current_user)]
)

# Define storage path
STORAGE_PATH = Path("storage/media_uploads")
STORAGE_PATH.mkdir(parents=True, exist_ok=True) # Ensure directory exists

@router.post("/upload", response_model=MediaItemInDB, status_code=status.HTTP_201_CREATED)
async def upload_media(current_user: Annotated[User, Depends(get_current_user)], file: UploadFile = File(...)):
    """
    Handles the upload of a media file (photo or video).
    It saves the file to the server and creates a metadata record in the database.
    """
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    storage_path = STORAGE_PATH / unique_filename

    try:
        with open(storage_path, "wb") as buffer:
            buffer.write(await file.read())
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    media_item = MediaItemInDB(
        owner_id=current_user.id,
        original_filename=file.filename,
        storage_path=str(storage_path),
        media_type=file.content_type,
    )

    db = load_db()
    add_media_item(db, media_item)
    save_db(db)

    return media_item

@router.get("/", response_model=List[MediaItemInDB])
async def list_user_media(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieves a list of all media items uploaded by the current user.
    """
    db = load_db()
    media_items_data = get_user_media(db, current_user.id)
    return [MediaItemInDB(**item) for item in media_items_data]

@router.delete("/all", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_user_media(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Deletes all media items and corresponding files for the current user.
    """
    db = load_db()
    
    paths_to_delete = delete_user_media(db, current_user.id)
    save_db(db)
    
    for path_str in paths_to_delete:
        try:
            absolute_path = ROOT_DIR / path_str
            if absolute_path.exists():
                os.remove(absolute_path)
        except OSError as e:
            print(f"Error deleting file {path_str}: {e}")
            
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# IMPORTANT: Specific routes must come before general routes.
# /download/{media_id} must be defined before /{media_id}.
@router.get("/download/{media_id}")
async def download_media_file(media_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Downloads a media file.
    Ensures the user owns the media item before allowing the download.
    """
    db = load_db()
    media_item = get_media_by_id(db, media_id)

    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found.")

    if media_item["owner_id"] != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to download this file.")

    file_path = ROOT_DIR / media_item["storage_path"]

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk.")

    return FileResponse(path=file_path, filename=media_item["original_filename"], media_type=media_item["media_type"])

@router.get("/{media_id}", response_model=MediaItemInDB)
async def get_single_media(media_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieves a single media item by its ID.
    Ensures the item belongs to the currently authenticated user.
    """
    db = load_db()
    media_item_data = get_media_by_id(db, media_id)

    if not media_item_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    if media_item_data["owner_id"] != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this media")

    return MediaItemInDB(**media_item_data)