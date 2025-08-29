from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from typing import List, Annotated, Dict, Any
import uuid
from pathlib import Path

from models.schemas import FilterItemInDB, User
from routers.auth import get_current_user
from utils.database import load_db, save_db, add_filter_item, get_filters_for_user, get_filter_by_id

# --- Router --- #
router = APIRouter(
    prefix="/filters",
    tags=["Filter Management"],
    dependencies=[Depends(get_current_user)]
)

# Define storage path
STORAGE_PATH = Path("storage/filter_uploads")
STORAGE_PATH.mkdir(parents=True, exist_ok=True) # Ensure directory exists

@router.post("/upload", response_model=FilterItemInDB, status_code=status.HTTP_201_CREATED)
async def upload_filter(current_user: Annotated[User, Depends(get_current_user)], file: UploadFile = File(...)):
    """
    Handles the upload of a custom filter file (e.g., a .cube LUT file).
    Saves the file and its metadata, marking it as a 'custom' filter owned by the user.
    """
    if not file.filename.endswith('.cube'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .cube files are accepted.")

    unique_filename = f"{uuid.uuid4()}.cube"
    storage_path = STORAGE_PATH / unique_filename

    try:
        with open(storage_path, "wb") as buffer:
            buffer.write(await file.read())
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Create metadata record for the filter
    filter_type = 'custom'
    owner_id = current_user.id

    if current_user.role == "admin":
        filter_type = "default"
        owner_id = None

    filter_item = FilterItemInDB(
        name=Path(file.filename).stem,
        storage_path=str(storage_path),
        filter_type=filter_type,
        owner_id=owner_id
    )

    db = load_db()
    add_filter_item(db, filter_item)
    save_db(db)

    return filter_item

# --- ✨ MODIFICATION START ✨ ---

@router.get("/", response_model=Dict[str, Any])
async def list_available_filters(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    """
    Retrieves a paginated list of filters available to the current user.
    This includes all 'default' filters and the user's own 'custom' filters.
    """
    db = load_db()
    
    # --- ✨ THIS IS THE CORRECTED LINE ✨ ---
    all_user_filters = get_filters_for_user(db, current_user.id, current_user.filter_usage)

    # 2. 計算總數
    total_items = len(all_user_filters)

    # 3. 根據 page 和 limit 計算要返回的資料切片 (slice)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_items = all_user_filters[start_index:end_index]

    # 4. 回傳一個包含分頁資訊的物件
    return {
        "total_items": total_items,
        "items": [FilterItemInDB(**item) for item in paginated_items],
        "page": page,
        "limit": limit
    }

# --- ✨ MODIFICATION END ✨ ---


@router.get("/{filter_id}", response_model=FilterItemInDB)
async def get_single_filter(filter_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieves a single filter by its ID.
    A user can retrieve any 'default' filter or a 'custom' filter that they own.
    """
    db = load_db()
    filter_item_data = get_filter_by_id(db, filter_id)

    if not filter_item_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filter not found")

    # Check for authorization
    is_default = filter_item_data.get("filter_type") == "default"
    is_owner = str(current_user.id) == filter_item_data.get("owner_id")

    if not is_default and not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this filter")

    return FilterItemInDB(**filter_item_data)