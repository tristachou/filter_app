from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from pathlib import Path
import uuid
import tempfile
import os # Import os for os.unlink

# App-specific imports
from models.schemas import ProcessRequest, ProcessResponse, MediaItemInDB
from routers.auth import get_current_user
from utils.database import load_db, save_db, get_media_by_id, get_filter_by_id, add_media_item
from services.process_media import apply_lut_to_image, apply_lut_to_video
from utils.s3_client import s3_client, S3_BUCKET_NAME, upload_file_to_s3

# --- Router --- #
router = APIRouter(
    prefix="/process",
    tags=["Processing"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=ProcessResponse)
async def apply_filter_to_media(
    request: ProcessRequest,
    user_claims: Dict = Depends(get_current_user)
):
    """
    Applies a LUT filter to a media file using FFmpeg, saves the result to S3,
    creates a new database entry for it, and returns the new media ID.
    """
    db = load_db()
    user_id = user_claims.get("sub")

    # --- 1. Validate Inputs ---
    media_item = get_media_by_id(db, request.media_id)
    if not media_item or media_item["owner_id"] != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media item not found or access denied.")

    filter_item = get_filter_by_id(db, request.filter_id)
    if not filter_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filter item not found.")

    is_default_filter = filter_item.get("filter_type") == "default"
    is_filter_owner = str(user_id) == filter_item.get("owner_id")
    if not is_default_filter and not is_filter_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this filter.")

    # --- 2. Prepare Paths and Download from S3 ---
    temp_input_file = None
    temp_filter_file = None
    temp_output_file = None

    try:
        # Download input media from S3 to a temporary file
        s3_input_key = media_item["storage_path"]
        file_suffix = Path(media_item["original_filename"]).suffix
        temp_input_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix)
        s3_client.download_fileobj(S3_BUCKET_NAME, s3_input_key, temp_input_file)
        temp_input_file.close() # Close to ensure content is flushed before ffmpeg reads

        # Download filter from S3 to a temporary file
        s3_filter_key = filter_item["storage_path"]
        temp_filter_file = tempfile.NamedTemporaryFile(delete=False, suffix=".cube")
        s3_client.download_fileobj(S3_BUCKET_NAME, s3_filter_key, temp_filter_file)
        temp_filter_file.close() # Close to ensure content is flushed before ffmpeg reads

        # Prepare temporary output file
        temp_output_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix)
        temp_output_file.close() # Close to ensure ffmpeg can write to it

        # --- 3. Execute Processing Logic ---
        print(f"[PROCESSING START] Applying filter {filter_item['name']} to {media_item['original_filename']}")
        
        success = False
        media_type = media_item.get("media_type", "")

        if "video" in media_type:
            success = apply_lut_to_video(temp_input_file.name, temp_filter_file.name, temp_output_file.name)
        elif "image" in media_type:
            success = apply_lut_to_image(temp_input_file.name, temp_filter_file.name, temp_output_file.name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported media type: {media_type}")

        if not success:
            raise HTTPException(status_code=500, detail="FFmpeg processing failed. Check server logs for details.")

        print(f"[PROCESSING FINISHED] Output saved to {temp_output_file.name}")

        # --- 4. Upload Processed Media to S3 ---
        s3_output_key = f"processed/{user_id}/{uuid.uuid4()}{file_suffix}"
        with open(temp_output_file.name, 'rb') as f: # Re-open for reading to upload
            upload_file_to_s3(f, s3_output_key, media_type)
        print(f"[UPLOADED TO S3] Processed media uploaded to {s3_output_key}")

        # TODO: Re-implement filter usage tracking.
        # The previous implementation modified a local user database which is now obsolete.
        # A new system would require a separate database to store app-specific user metadata,
        # linked by the Cognito user ID (the 'sub' claim).
        # For now, this functionality is disabled.
        # --- Increment filter usage count block removed ---

        # --- 5. Save New Media Item to Database ---
        processed_media_item = MediaItemInDB(
            owner_id=user_id,
            original_filename=f"{Path(media_item['original_filename']).stem}_processed{file_suffix}",
            storage_path=s3_output_key, # Store S3 object key
            media_type=media_type,
        )
        add_media_item(db, processed_media_item)
        save_db(db)

        # --- 6. Return Response with New ID ---
        return ProcessResponse(
            message="Filter application process completed successfully.",
            processed_media_id=processed_media_item.id,
            processed_filename=processed_media_item.original_filename
        )

    except Exception as e:
        print(f"Error during media processing or S3 interaction: {e}")
        raise HTTPException(status_code=500, detail=f"A critical error occurred: {e}")
    finally:
        # Clean up temporary files
        if temp_input_file and os.path.exists(temp_input_file.name):
            os.unlink(temp_input_file.name)
        if temp_filter_file and os.path.exists(temp_filter_file.name):
            os.unlink(temp_filter_file.name)
        if temp_output_file and os.path.exists(temp_output_file.name):
            os.unlink(temp_output_file.name)
