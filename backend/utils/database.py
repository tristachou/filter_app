import json
from pathlib import Path
from typing import Dict, Any, Union
from uuid import UUID
import os

from models.schemas import MediaItemInDB, FilterItemInDB, User

# Define the root directory of the application
# This is set to the parent directory of the current file (utils)
ROOT_DIR = Path(__file__).parent.parent
DB_PATH = ROOT_DIR / "db.json"

def load_db() -> Dict[str, Any]:
    """
    Loads the JSON database from the file system.
    If the database file does not exist, it initializes it with default users.
    """
    if not DB_PATH.exists():
        print("Database file not found. Initializing with default data.")
        # Hardcoded users for initial setup
        users = [
            {"id": "a7b8b5e0-5c6e-4e8a-9b9a-6a2b3c4d5e6f", "username": "user1", "hashed_password": "fake_password_1", "role": "admin"},
            {"id": "b8c9c6f1-6d7f-5f9b-a0a0-7b3c4d5e6f7f", "username": "user2", "hashed_password": "fake_password_2", "role": "user"},
        ]
        db_data = {
            "users": {user["id"]: user for user in users},
            "media_items": {},
            "filter_items": {},
        }

        _seed_default_filters(db_data)
    
    
        save_db(db_data)
        return db_data
    
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data: Dict[str, Any]):
    """
    Saves the given dictionary to the JSON database file.
    """
    with open(DB_PATH, "w") as f:
        # Use a custom JSON encoder to handle UUID and other complex types
        json.dump(data, f, indent=4, default=str)

# --- Media Item Functions ---

def get_media_by_id(db: Dict[str, Any], media_id: UUID) -> Union[Dict[str, Any], None]:
    """Retrieves a media item by its ID."""
    return db["media_items"].get(str(media_id))

def add_media_item(db: Dict[str, Any], media_item: MediaItemInDB) -> MediaItemInDB:
    """Adds a new media item to the database."""
    db["media_items"][str(media_item.id)] = media_item.model_dump()
    return media_item

def get_user_media(db: Dict[str, Any], user_id: UUID) -> list[Dict[str, Any]]:
    """Retrieves all PROCESSED media items for a specific user."""
    user_items = []
    for item in db["media_items"].values():
        # Only return items that belong to the user AND are processed files
        
        if item["owner_id"] == str(user_id):
            user_items.append(item)
    return user_items

def delete_user_media(db: Dict[str, Any], user_id: UUID) -> list[str]:
    """
    Deletes all media items for a specific user from the database.
    Returns a list of storage paths for the files to be deleted from disk.
    """
    items_to_delete = [item for item in db["media_items"].values() if item["owner_id"] == str(user_id)]
    
    paths_to_delete = [item["storage_path"] for item in items_to_delete]
    
    for item in items_to_delete:
        del db["media_items"][item["id"]]
        
    return paths_to_delete

def _seed_default_filters(db: Dict[str, Any]):
    """
    Scans the default LUTs directory and adds any new filters to the database.
    This is intended to be run at application startup.
    """
    default_luts_path = ROOT_DIR / "assets" / "luts"
    if not default_luts_path.exists():
        return 
    existing_paths = {item["storage_path"] for item in db["filter_items"].values()}
    

    for lut_file in default_luts_path.glob("*"):
      
        if lut_file.suffix.lower() == '.cube':
            
            relative_path = str(lut_file.relative_to(ROOT_DIR))

            if relative_path not in existing_paths:
                print(f"Found new default filter, adding to DB: {lut_file.name}")
                filter_item = FilterItemInDB(
                    name=lut_file.stem,  
                    storage_path=relative_path,
                    filter_type="default",
                    owner_id=None
                )
                add_filter_item(db, filter_item)



# --- Filter Item Functions ---

def get_filter_by_id(db: Dict[str, Any], filter_id: UUID) -> Union[Dict[str, Any], None]:
    """Retrieves a filter item by its ID."""
    return db["filter_items"].get(str(filter_id))

def add_filter_item(db: Dict[str, Any], filter_item: FilterItemInDB) -> FilterItemInDB:
    """Adds a new filter item to the database."""
    db["filter_items"][str(filter_item.id)] = filter_item.model_dump()
    return filter_item

def get_filters_for_user(db: Dict[str, Any], user_id: UUID, user_filter_usage: Dict[str, int]) -> list[Dict[str, Any]]:
    """
    Retrieves all default filters plus all filters owned by the specified user,
    sorted by the user's usage count in descending order.
    """
    visible_filters = []
    for item in db["filter_items"].values():
        # A filter is visible if it's a default filter OR if the user is the owner
        if item.get("filter_type") == "default" or item.get("owner_id") == str(user_id):
            # Create a copy of the item to avoid modifying the original db object
            item_copy = item.copy()
            
            # Get user-specific usage count, default to 0 if not found
            filter_id_str = str(item_copy["id"]) # Ensure filter ID is a string for dictionary lookup
            item_usage_count = user_filter_usage.get(filter_id_str, 0)
            
            # Add usage count to the item_copy for sorting purposes (temporarily)
            item_copy["_user_usage_count"] = item_usage_count
            visible_filters.append(item_copy)
            
    # Sort filters by user-specific usage count in descending order
    visible_filters.sort(key=lambda x: x.get("_user_usage_count", 0), reverse=True)
    
    # Remove the temporary _user_usage_count key before returning
    for item in visible_filters:
        if "_user_usage_count" in item:
            del item["_user_usage_count"]
            
    return visible_filters

# --- User Functions ---

def get_user_by_username(db: Dict[str, Any], username: str) -> Union[User, None]:
    """Retrieves a user by their username."""
    for user_data in db["users"].values():
        if user_data["username"] == username:
            return User(**user_data)
    return None

def get_user_by_id(db: Dict[str, Any], user_id: UUID) -> Union[User, None]:
    """Retrieves a user by their ID."""
    user_data = db["users"].get(str(user_id))
    if user_data:
        return User(**user_data)
    return None