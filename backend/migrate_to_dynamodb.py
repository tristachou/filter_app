
import os
import json
import boto3
from decimal import Decimal

# This is a one-time script to migrate data from the local db.json file
# to the newly created DynamoDB tables.

def migrate_data_to_dynamodb():
    """
    Reads users, media_items, and filter_items from db.json and writes them
    to their respective DynamoDB tables.
    """
    # --- Configuration ---
    STUDENT_ID_PREFIX = os.getenv("STUDENT_ID_PREFIX", "n11696630-")
    AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
    DB_JSON_PATH = os.path.join(os.path.dirname(__file__), "db.json")

    # --- Initialization ---
    print("Connecting to DynamoDB...")
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        users_table = dynamodb.Table(f"{STUDENT_ID_PREFIX}users")
        media_items_table = dynamodb.Table(f"{STUDENT_ID_PREFIX}media_items")
        filter_items_table = dynamodb.Table(f"{STUDENT_ID_PREFIX}filter_items")
        print("Connection successful.")
    except Exception as e:
        print(f"\033[91mError connecting to DynamoDB: {e}. Please check credentials and region.\033[0m")
        return

    if not os.path.exists(DB_JSON_PATH):
        print(f"\033[91mError: db.json not found at '{DB_JSON_PATH}'. Nothing to migrate.\033[0m")
        return

    print(f"Loading data from {DB_JSON_PATH}...")
    with open(DB_JSON_PATH, 'r') as f:
        db_data = json.load(f)

    # Helper to convert floats to Decimals for DynamoDB
    def floats_to_decimals(obj):
        if isinstance(obj, list):
            return [floats_to_decimals(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: floats_to_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, float):
            return Decimal(str(obj))
        return obj



    # --- Migrate Filter Items ---
    filter_items = list(db_data.get("filter_items", {}).values())
    if filter_items:
        print(f"\nMigrating {len(filter_items)} filter items...")
        try:
            with filter_items_table.batch_writer() as batch:
                for item in filter_items:
                    item_decimal = floats_to_decimals(item)
                    batch.put_item(Item=item_decimal)
            print(f"  \033[92mSuccessfully migrated {len(filter_items)} filter items.\033[0m")
        except Exception as e:
            print(f"  \033[91mError migrating filter items: {e}\033[0m")
    else:
        print("\nNo filter items found to migrate.")

    print("\n--- Data migration complete! ---")

if __name__ == "__main__":
    migrate_data_to_dynamodb()
