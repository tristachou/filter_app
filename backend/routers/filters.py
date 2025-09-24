from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from typing import Dict, Any, List
import uuid
from pathlib import Path

from models.schemas import FilterItemInDB
from routers.auth import get_current_user
# Import the new DynamoDB-based functions
from utils.database import add_filter_item, get_filters_for_user, get_filter_by_id
from utils.s3_client import upload_file_to_s3

# --- Router --- #
router = APIRouter(
    prefix="/filters",
    tags=["Filter Management"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/upload", response_model=FilterItemInDB, status_code=status.HTTP_201_CREATED)
async def upload_filter(user_claims: Dict = Depends(get_current_user), file: UploadFile = File(...)):
    """
    Handles the upload of a custom filter file (e.g., a .cube LUT file) to S3.
    Saves the file to the appropriate S3 path and its metadata to DynamoDB.
    """
    if not file.filename.endswith('.cube'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .cube files are accepted.")

    user_id = user_claims.get("sub")
    user_groups = user_claims.get("cognito:groups", [])

    # Determine S3 path and metadata based on user role
    if "admin" in user_groups:
        object_key = f"filters/public/{uuid.uuid4()}.cube"
        filter_type = "default"
        owner_id = None
    else:
        object_key = f"filters/user/{user_id}/{uuid.uuid4()}.cube"
        filter_type = "custom"
        owner_id = user_id

    # Upload file to S3
    upload_file_to_s3(file.file, object_key, file.content_type)

    # Create metadata record for the filter
    filter_item = FilterItemInDB(
        name=Path(file.filename).stem,
        storage_path=object_key,
        filter_type=filter_type,
        owner_id=owner_id
    )

    # Add the new filter item to DynamoDB
    add_filter_item(filter_item.model_dump())

    return filter_item

@router.get("/", response_model=Dict[str, Any])
async def list_available_filters(
    user_claims: Dict = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    """
    Retrieves a paginated list of filters available to the current user from DynamoDB.
    """
    user_id = user_claims.get("sub")
    
    # Get all filters available to this user from DynamoDB
    all_user_filters = get_filters_for_user(user_id)

    # --- Pagination Logic (remains the same) ---
    total_items = len(all_user_filters)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_items = all_user_filters[start_index:end_index]

    return {
        "total_items": total_items,
        "items": [FilterItemInDB(**item) for item in paginated_items],
        "page": page,
        "limit": limit
    }

@router.get("/{filter_id}", response_model=FilterItemInDB)
async def get_single_filter(filter_id: uuid.UUID, user_claims: Dict = Depends(get_current_user)):
    """
    Retrieves a single filter by its ID from DynamoDB.
    """
    filter_item_data = get_filter_by_id(filter_id)

    if not filter_item_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filter not found")

    # Check for authorization
    user_id = user_claims.get("sub")
    is_default = filter_item_data.get("filter_type") == "default"
    is_owner = str(user_id) == filter_item_data.get("owner_id")

    if not is_default and not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this filter")

    return FilterItemInDB(**filter_item_data)