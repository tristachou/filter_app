import boto3
import os
import json
import logging
import time
from botocore.exceptions import ClientError

from process_logic import apply_lut_to_video, apply_lut_to_image
from worker_schemas import MediaItemInDB
from database_utils import add_media_item
from uuid import UUID # Needed for MediaItemInDB

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# AWS Clients
sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION', 'ap-southeast-2'))
s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'ap-southeast-2'))

# Configuration from environment variables
SQS_QUEUE_URL = "https://sqs.ap-southeast-2.amazonaws.com/901444280953/n11696630"# os.environ.get('SQS_QUEUE_URL')
S3_BUCKET_NAME = "n11696630" #os.environ.get('S3_BUCKET_NAME')
LUT_DIRECTORY = os.environ.get('LUT_DIRECTORY', '/app/assets/luts') # Default path inside container

if not SQS_QUEUE_URL:
    logger.error("SQS_QUEUE_URL environment variable not set.")
    exit(1)
if not S3_BUCKET_NAME:
    logger.error("S3_BUCKET_NAME environment variable not set.")
    exit(1)

def download_from_s3(bucket: str, key: str, local_path: str) -> bool:
    """Downloads a file from S3 to a local path."""
    try:
        s3_client.download_file(bucket, key, local_path)
        logger.info(f"Downloaded s3://{bucket}/{key} to {local_path}")
        return True
    except ClientError as e:
        logger.error(f"Error downloading {key} from S3: {e}")
        return False

def upload_to_s3(bucket: str, key: str, local_path: str) -> bool:
    """Uploads a file from a local path to S3."""
    try:
        s3_client.upload_file(local_path, bucket, key)
        logger.info(f"Uploaded {local_path} to s3://{bucket}/{key}")
        return True
    except ClientError as e:
        logger.error(f"Error uploading {local_path} to S3: {e}")
        return False

def process_message(message_body: dict):
    """Processes a single SQS message."""
    s3_input_key = message_body.get('s3_input_key')
    s3_output_key = message_body.get('s3_output_key')
    lut_filename = message_body.get('lut_filename')
    media_type = message_body.get('media_type') # 'video' or 'image'
    crf = message_body.get('crf', 23) # For video
    quality = message_body.get('quality', 2) # For image

    if not all([s3_input_key, s3_output_key, lut_filename, media_type]):
        logger.error(f"Invalid message body: {message_body}. Missing required fields.")
        return False

    # Construct local paths
    local_input_path = f"/tmp/{os.path.basename(s3_input_key)}"
    local_output_path = f"/tmp/{os.path.basename(s3_output_key)}"
    lut_path = os.path.join(LUT_DIRECTORY, lut_filename)

    # Ensure LUT file exists
    if not os.path.exists(lut_path):
        logger.error(f"LUT file not found: {lut_path}")
        return False

    # Download input file from S3
    if not download_from_s3(S3_BUCKET_NAME, s3_input_key, local_input_path):
        return False

    # Process media
    success = False
    if 'video' in media_type: # Check if 'video' is in the MIME type
        success = apply_lut_to_video(local_input_path, lut_path, local_output_path, crf)
    elif 'image' in media_type: # Check if 'image' is in the MIME type
        success = apply_lut_to_image(local_input_path, lut_path, local_output_path, quality)
    else:
        logger.error(f"Unsupported media type: {media_type}")

    if not success:
        logger.error(f"Media processing failed for {s3_input_key}")
        # Clean up local files even if processing failed
        if os.path.exists(local_input_path):
            os.remove(local_input_path)
        if os.path.exists(local_output_path):
            os.remove(local_output_path)
        return False

    # Upload output file to S3
    if not upload_to_s3(S3_BUCKET_NAME, s3_output_key, local_output_path):
        # Clean up local files
        if os.path.exists(local_input_path):
            os.remove(local_input_path)
        if os.path.exists(local_output_path):
            os.remove(local_output_path)
        return False

    # Clean up local files
    if os.path.exists(local_input_path):
        os.remove(local_input_path)
    if os.path.exists(local_output_path):
        os.remove(local_output_path)
    
    logger.info(f"Successfully processed and uploaded {s3_input_key} to {s3_output_key}")

    # --- 5. Save New Media Item to DynamoDB ---
    try:
        processed_media_item = MediaItemInDB(
            owner_id=UUID(message_body["user_id"]),
            original_filename=f"{os.path.splitext(message_body['original_filename'])[0]}_processed{os.path.splitext(s3_output_key)[1]}",
            storage_path=s3_output_key,
            media_type=media_type,
            is_processed=True,
            original_media_id=UUID(message_body["media_id"])
        )
        add_media_item(processed_media_item.model_dump())
        logger.info(f"Added processed media item {processed_media_item.id} to DynamoDB.")
    except Exception as e:
        logger.error(f"Error adding processed media item to DynamoDB: {e}", exc_info=True)
        # If DB update fails, we don't want to delete the SQS message,
        # so it can be retried.
        return False

    return True

def main():
    logger.info("Media Worker started. Polling SQS queue...")
    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20 # Long polling
            )

            messages = response.get('Messages', [])
            if not messages:
                logger.info("No messages in queue. Waiting...")
                continue

            for message in messages:
                receipt_handle = message['ReceiptHandle']
                try:
                    message_body = json.loads(message['Body'])
                    logger.info(f"Received message: {message_body}")
                    
                    if process_message(message_body):
                        sqs_client.delete_message(
                            QueueUrl=SQS_QUEUE_URL,
                            ReceiptHandle=receipt_handle
                        )
                        logger.info(f"Message {message['MessageId']} deleted from queue.")
                    else:
                        logger.warning(f"Failed to process message {message['MessageId']}. It will become visible again.")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in message body: {message['Body']}. Deleting message to prevent reprocessing.")
                    sqs_client.delete_message(
                        QueueUrl=SQS_QUEUE_URL,
                        ReceiptHandle=receipt_handle
                    )
                except Exception as e:
                    logger.error(f"An unexpected error occurred while processing message {message.get('MessageId', 'N/A')}: {e}", exc_info=True)
                    # Message will become visible again after VisibilityTimeout
        except ClientError as e:
            logger.error(f"AWS Client Error: {e}")
            time.sleep(60) # Wait before retrying to avoid hammering AWS
        except Exception as e:
            logger.error(f"An unexpected error occurred in main loop: {e}", exc_info=True)
            time.sleep(60) # Wait before retrying

if __name__ == "__main__":
    main()
