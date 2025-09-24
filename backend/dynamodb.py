import boto3
from botocore.exceptions import ClientError

qut_username = "n11696630@qut.edu.au"  # Change to your own username
region = "ap-southeast-2"
table_name = "n11696630"  # Change to your own username
sort_key = "name"

dynamodb = boto3.client("dynamodb", region_name=region)


def create_table():
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {"AttributeName": "qut-username", "AttributeType": "S"},
                {"AttributeName": sort_key, "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "qut-username", "KeyType": "HASH"},
                {"AttributeName": sort_key, "KeyType": "RANGE"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        print("Create Table response:", response)
    except ClientError as e:
        print(e)

create_table()


def get_item():
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                "qut-username": {"S": qut_username},
                sort_key: {"S": "Boots"},
            },
        )
        print("Item data:", response.get("Item"))
    except ClientError as e:
        print(e)
get_item()

def query_items():
    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="#pk = :username AND begins_with(#sk, :nameStart)",
            ExpressionAttributeNames={"#pk": "qut-username", "#sk": sort_key},
            ExpressionAttributeValues={":username": {"S": qut_username}, ":nameStart": {"S": "Boo"}},
        )
        print("Query found these items:", response.get("Items"))
    except ClientError as e:
        print(e)

query_items()