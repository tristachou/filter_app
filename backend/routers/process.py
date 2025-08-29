from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from pathlib import Path
import uuid

# App-specific imports
from models.schemas import ProcessRequest, ProcessResponse, User, MediaItemInDB
from routers.auth import get_current_user
from utils.database import load_db, save_db, get_media_by_id, get_filter_by_id, add_media_item, ROOT_DIR
from services.process_media import apply_lut_to_image, apply_lut_to_video

# --- Router --- #
router = APIRouter(
    prefix="/process",
    tags=["Processing"],
    dependencies=[Depends(get_current_user)]
)

# Define output path
PROCESSED_STORAGE_PATH = Path("storage/processed_output")
PROCESSED_STORAGE_PATH.mkdir(parents=True, exist_ok=True) # Ensure directory exists

@router.post("/", response_model=ProcessResponse)
async def apply_filter_to_media(
    request: ProcessRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Applies a LUT filter to a media file using FFmpeg, saves the result,
    creates a new database entry for it, and returns the new media ID.
    """
    db = load_db()

    # --- 1. Validate Inputs ---
    media_item = get_media_by_id(db, request.media_id)
    if not media_item or media_item["owner_id"] != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media item not found or access denied.")

    filter_item = get_filter_by_id(db, request.filter_id)
    if not filter_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filter item not found.")

    is_default_filter = filter_item.get("filter_type") == "default"
    is_filter_owner = str(current_user.id) == filter_item.get("owner_id")
    if not is_default_filter and not is_filter_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this filter.")

    # --- 2. Prepare Paths ---
    input_media_path = ROOT_DIR / media_item["storage_path"]
    lut_file_path = ROOT_DIR / filter_item["storage_path"]
    
    # Generate a unique name for the output file
    file_suffix = Path(media_item["original_filename"]).suffix
    output_filename = f"processed_{uuid.uuid4()}{file_suffix}"
    # Ensure the output path is absolute from the start
    output_media_path = ROOT_DIR / PROCESSED_STORAGE_PATH / output_filename

    # --- 3. Execute Processing Logic ---
    print(f"[PROCESSING START] Applying filter {filter_item['name']} to {media_item['original_filename']}")
    
    success = False
    media_type = media_item.get("media_type", "")

    try:
        if "video" in media_type:
            success = apply_lut_to_video(str(input_media_path), str(lut_file_path), str(output_media_path))
        elif "image" in media_type:
            success = apply_lut_to_image(str(input_media_path), str(lut_file_path), str(output_media_path))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported media type: {media_type}")
    except Exception as e:
        # Catch potential errors from the processing script
        print(f"Error during media processing: {e}")
        raise HTTPException(status_code=500, detail="A critical error occurred during media processing.")

    if not success:
        raise HTTPException(status_code=500, detail="FFmpeg processing failed. Check server logs for details.")

    print(f"[PROCESSING FINISHED] Output saved to {output_media_path}")

    # --- Increment filter usage count for the current user ---
    # Find the user in the database's user list
    for user_data in db["users"].values():
        if user_data["id"] == str(current_user.id):
            # Ensure filter_usage exists and is a dictionary
            if "filter_usage" not in user_data or not isinstance(user_data["filter_usage"], dict):
                user_data["filter_usage"] = {}
            
            filter_id_str = str(request.filter_id)
            user_data["filter_usage"][filter_id_str] = user_data["filter_usage"].get(filter_id_str, 0) + 1
            break # User found and updated, exit loop

    # --- 4. Save New Media Item to Database ---
    processed_media_item = MediaItemInDB(
        owner_id=current_user.id,
        original_filename=f"{Path(media_item['original_filename']).stem}_processed{file_suffix}",
        storage_path=str(output_media_path.relative_to(ROOT_DIR)), # Store relative path
        media_type=media_type,
    )
    add_media_item(db, processed_media_item)
    save_db(db)

    # --- 5. Return Response with New ID ---
    return ProcessResponse(
        message="Filter application process completed successfully.",
        processed_media_id=processed_media_item.id,
        processed_filename=processed_media_item.original_filename
    )