
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, Any, Union, List
from uuid import UUID

# --- DynamoDB Setup ---
# Using an environment variable for the prefix is a good practice for production
STUDENT_ID_PREFIX = "n11696630-" # Hardcoding to ensure consistency
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

USERS_TABLE = dynamodb.Table(f"{STUDENT_ID_PREFIX}users")
MEDIA_ITEMS_TABLE = dynamodb.Table(f"{STUDENT_ID_PREFIX}media_items")
FILTER_ITEMS_TABLE = dynamodb.Table(f"{STUDENT_ID_PREFIX}filter_items")

# --- User Functions ---

def get_user_by_id(user_id: UUID) -> Union[Dict[str, Any], None]:
    """Retrieves a user by their ID from DynamoDB."""
    try:
        response = USERS_TABLE.get_item(Key={'id': str(user_id)})
        return response.get('Item')
    except Exception as e:
        print(f"Error getting user {user_id}: {e}")
        return None

def get_user_by_username(username: str) -> Union[Dict[str, Any], None]:
    """Retrieves a user by their username using a scan operation."""
    # Note: A scan is inefficient for large tables. For production, a GSI on 'username' would be better.
    try:
        response = USERS_TABLE.scan(FilterExpression=Attr('username').eq(username))
        items = response.get('Items', [])
        return items[0] if items else None
    except Exception as e:
        print(f"Error scanning for user {username}: {e}")
        return None

# --- Media Item Functions ---

def get_media_by_id(media_id: UUID) -> Union[Dict[str, Any], None]:
    """Retrieves a single media item by its ID from DynamoDB."""
    try:
        response = MEDIA_ITEMS_TABLE.get_item(Key={'id': str(media_id)})
        return response.get('Item')
    except Exception as e:
        print(f"Error getting media item {media_id}: {e}")
        return None

from datetime import datetime

def _serialize_item_for_dynamodb(obj: Any) -> Any:
    """Recursively converts special types in a dictionary or list to DynamoDB-compatible formats."""
    if isinstance(obj, dict):
        return {k: _serialize_item_for_dynamodb(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_item_for_dynamodb(i) for i in obj]
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat() # Convert datetime to ISO 8601 string
    return obj

def add_media_item(media_item_dict: Dict[str, Any]):
    """Adds a new media item to the media_items table in DynamoDB."""
    try:
        # Convert any special types to strings before sending to DynamoDB
        item_to_add = _serialize_item_for_dynamodb(media_item_dict)
        MEDIA_ITEMS_TABLE.put_item(Item=item_to_add)
    except Exception as e:
        print(f"Error adding media item: {e}")
        # Re-raise to be caught by FastAPI error handling
        raise

def get_user_media(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all media items for a specific user using the GSI."""
    try:
        response = MEDIA_ITEMS_TABLE.query(
            IndexName='OwnerIdIndex',
            KeyConditionExpression=Key('owner_id').eq(user_id)
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error querying user media for {user_id}: {e}")
        return []

def delete_user_media(user_id: str) -> List[str]:
    """Finds all media for a user, collects their S3 paths, and deletes the items from DynamoDB."""
    paths_to_delete = []
    items_to_delete_keys = []
    
    # Find all media items for the user (both original and processed)
    user_media_items = get_user_media(user_id)
    
    for item in user_media_items:
        paths_to_delete.append(item['storage_path'])
        items_to_delete_keys.append({'id': item['id']})

    # Delete items from DynamoDB in a batch for efficiency
    if items_to_delete_keys:
        try:
            with MEDIA_ITEMS_TABLE.batch_writer() as batch:
                for key in items_to_delete_keys:
                    batch.delete_item(Key=key)
        except Exception as e:
            print(f"Error batch deleting media items from DynamoDB: {e}")
            # If DB deletion fails, do not return paths to prevent orphaning S3 files
            return []
            
    return paths_to_delete

# --- Filter Item Functions ---

def get_filter_by_id(filter_id: UUID) -> Union[Dict[str, Any], None]:
    """Retrieves a single filter item by its ID from DynamoDB."""
    try:
        response = FILTER_ITEMS_TABLE.get_item(Key={'id': str(filter_id)})
        return response.get('Item')
    except Exception as e:
        print(f"Error getting filter item {filter_id}: {e}")
        return None

def add_filter_item(filter_item_dict: Dict[str, Any]):
    """Adds a new filter item to the filter_items table in DynamoDB."""
    try:
        item_to_add = _serialize_item_for_dynamodb(filter_item_dict)
        FILTER_ITEMS_TABLE.put_item(Item=item_to_add)
    except Exception as e:
        print(f"Error adding filter item: {e}")
        raise

def get_filters_for_user(user_id: UUID, **kwargs) -> List[Dict[str, Any]]:
    """Retrieves all default filters plus all filters owned by the specified user."""
    try:
        # 1. Get all default filters using the GSI
        default_filters_response = FILTER_ITEMS_TABLE.query(
            IndexName='FilterTypeIndex',
            KeyConditionExpression=Key('filter_type').eq('default')
        )
        visible_filters = default_filters_response.get('Items', [])

        # 2. Get user's own custom filters using a scan
        # Note: Inefficient for many custom filters. A GSI on owner_id would be better.
        custom_filters_response = FILTER_ITEMS_TABLE.scan(
            FilterExpression=Attr('owner_id').eq(str(user_id))
        )
        visible_filters.extend(custom_filters_response.get('Items', []))
        
        return visible_filters
    except Exception as e:
        print(f"Error getting filters for user {user_id}: {e}")
        return []
