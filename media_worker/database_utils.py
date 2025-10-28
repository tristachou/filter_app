import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, Any, Union, List
from uuid import UUID, uuid4 # Import uuid4 for default_factory
from datetime import datetime

# --- DynamoDB Setup ---
STUDENT_ID_PREFIX = "n11696630-" # Hardcoding to ensure consistency
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

MEDIA_ITEMS_TABLE = dynamodb.Table(f"{STUDENT_ID_PREFIX}media_items")

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
        raise
