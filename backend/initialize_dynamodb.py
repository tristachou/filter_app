import boto3
from botocore.exceptions import ClientError
import os

# This script initializes the DynamoDB tables required for the application.
# It is idempotent, meaning it can be run multiple times without causing errors;
# it will only create tables that do not already exist.

# --- Configuration ---
STUDENT_ID_PREFIX = os.getenv("STUDENT_ID_PREFIX", "n11696630-") # Using hyphen as confirmed
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
PROVISIONED_THROUGHPUT = {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}

# --- Table Definitions ---
# This list contains the complete and correct schema for each table.
TABLE_DEFINITIONS = [
    {
        "TableName": f"{STUDENT_ID_PREFIX}users",
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}],
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
    },
    {
        "TableName": f"{STUDENT_ID_PREFIX}media_items",
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "owner_id", "AttributeType": "S"}
        ],
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "GlobalSecondaryIndexes": [{
            "IndexName": "OwnerIdIndex",
            "KeySchema": [{"AttributeName": "owner_id", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
            "ProvisionedThroughput": PROVISIONED_THROUGHPUT
        }],
    },
    {
        "TableName": f"{STUDENT_ID_PREFIX}filter_items",
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "filter_type", "AttributeType": "S"}
        ],
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "GlobalSecondaryIndexes": [{
            "IndexName": "FilterTypeIndex",
            "KeySchema": [{"AttributeName": "filter_type", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
            "ProvisionedThroughput": PROVISIONED_THROUGHPUT
        }],
    }
]

def create_dynamodb_tables():
    """
    Iterates through the table definitions and creates them in DynamoDB.
    """
    try:
        dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
        print(f"Connected to DynamoDB in region: {AWS_REGION}")
    except ClientError as e:
        print(f"\033[91mError connecting to AWS. Please check your credentials. {e}\033[0m")
        return

    for table_def in TABLE_DEFINITIONS:
        table_name = table_def["TableName"]
        # Add provisioned throughput to the base definition
        table_def["ProvisionedThroughput"] = PROVISIONED_THROUGHPUT
        
        try:
            print(f"\nAttempting to create table '{table_name}'...")
            dynamodb.create_table(**table_def)
            
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name, WaiterConfig={'Delay': 5, 'MaxAttempts': 10})
            
            print(f"  \033[92mSuccess! Table '{table_name}' created.\033[0m")

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceInUseException":
                print(f"  \033[93mInfo: Table '{table_name}' already exists. Skipping.\033[0m")
            else:
                print(f"  \033[91mError creating table '{table_name}': {e}\033[0m")

    print("\nInitialization complete.")

if __name__ == "__main__":
    create_dynamodb_tables()