from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from pathlib import Path
import uuid
import tempfile
import os

# App-specific imports
from models.schemas import ProcessRequest, ProcessResponse, MediaItemInDB
from routers.auth import get_current_user
# Import the new DynamoDB-based functions
from utils.database import get_media_by_id, get_filter_by_id, add_media_item
import json # Added for SQS message body
import boto3 # Added for SQS interaction

# App-specific imports
from models.schemas import ProcessRequest, ProcessResponse, MediaItemInDB
from routers.auth import get_current_user
from utils.database import get_media_by_id, get_filter_by_id, add_media_item
# Removed direct import of process_media service
# from services.process_media import apply_lut_to_image, apply_lut_to_video
from utils.s3_client import s3_client, S3_BUCKET_NAME, upload_file_to_s3

# --- Router --- #
router = APIRouter(
    prefix="/process",
    tags=["Processing"],
    dependencies=[Depends(get_current_user)]
)

# SQS Client and Queue URL (should be configured via environment variables)
sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION', 'ap-southeast-2'))
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

if not SQS_QUEUE_URL:
    raise RuntimeError("SQS_QUEUE_URL environment variable not set for backend API.")

@router.post("/", response_model=ProcessResponse)
async def apply_filter_to_media(
    request: ProcessRequest,
    user_claims: Dict = Depends(get_current_user)
):
    """
    Submits a request to apply a LUT filter to a media file to an SQS queue.
    The actual processing will be handled by a separate worker.
    """
    user_id = user_claims.get("sub")

    # --- 1. Validate Inputs from DynamoDB ---
    media_item = get_media_by_id(request.media_id)
    if not media_item or media_item["owner_id"] != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media item not found or access denied.")

    filter_item = get_filter_by_id(request.filter_id)
    if not filter_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filter item not found.")

    is_default_filter = filter_item.get("filter_type") == "default"
    is_filter_owner = str(user_id) == filter_item.get("owner_id")
    if not is_default_filter and not is_filter_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this filter.")

    # --- Prepare data for SQS message ---
    s3_input_key = media_item["storage_path"]
    s3_filter_key = filter_item["storage_path"]
    file_suffix = Path(media_item["original_filename"]).suffix
    media_type = media_item.get("media_type", "")

    if "video" not in media_type and "image" not in media_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported media type: {media_type}")

    # Extract LUT filename from s3_filter_key
    lut_filename = Path(s3_filter_key).name

    # Generate a unique output key for the processed media
    s3_output_key = f"processed/{user_id}/{uuid.uuid4().hex}{file_suffix}"

    message_body = {
        "user_id": str(user_id),
        "media_id": str(request.media_id),  # Explicitly convert to string
        "filter_id": str(request.filter_id), # Explicitly convert to string
        "s3_input_key": s3_input_key,
        "s3_output_key": s3_output_key,
        "lut_filename": lut_filename,
        "media_type": media_type,
        "original_filename": media_item["original_filename"]
        # Add other parameters like crf, quality if needed and available in request
    }

    try:
        # --- Send message to SQS ---
        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message_body)
        )
        message_id = response['MessageId']
        print(f"[SQS MESSAGE SENT] MessageId: {message_id} for processing {s3_input_key}")

        # --- Return 202 Accepted response ---
        return ProcessResponse(
            message="Media processing request submitted successfully.",
            task_id=message_id # Use SQS MessageId as task_id for tracking
        )

    except Exception as e:
        print(f"Error sending message to SQS: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit processing request: {e}")

    # Removed all local file operations, direct processing calls, S3 uploads, and DynamoDB updates
    # These are now handled by the media_worker