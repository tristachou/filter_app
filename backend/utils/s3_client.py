import boto3
import os
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

# Load S3 bucket name from environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Initialize S3 client
try:
    s3_client = boto3.client("s3")
except Exception as e:
    print(f"Error initializing S3 client: {e}")
    # In a real application, you might want to handle this more gracefully
    # For now, we'll let it fail if credentials aren't set up.


def upload_file_to_s3(file_object, object_key: str, content_type: str):
    """
    Uploads a file-like object to S3.

    Args:
        file_object: A file-like object (e.g., from UploadFile.file).
        object_key: The S3 object key (path/filename).
        content_type: The MIME type of the file.

    Returns:
        The S3 object key if successful.

    Raises:
        HTTPException: If the upload fails.
    """
    if not S3_BUCKET_NAME:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3_BUCKET_NAME is not configured.")
    
    try:
        s3_client.upload_fileobj(
            file_object, 
            S3_BUCKET_NAME, 
            object_key, 
            ExtraArgs={'ContentType': content_type}
        )
        return object_key
    except ClientError as e:
        print(f"S3 upload failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file to S3: {e}")


def create_presigned_url(object_key: str, expiration: int = 3600):
    """
    Generate a pre-signed URL to share an S3 object.

    Args:
        object_key: The S3 object key.
        expiration: Time in seconds for the pre-signed URL to remain valid.

    Returns:
        The pre-signed URL as a string.

    Raises:
        HTTPException: If URL generation fails.
    """
    if not S3_BUCKET_NAME:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3_BUCKET_NAME is not configured.")

    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': S3_BUCKET_NAME,
                                                            'Key': object_key},
                                                    ExpiresIn=expiration)
        return response
    except ClientError as e:
        print(f"S3 pre-signed URL generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate pre-signed URL: {e}")

def delete_file_from_s3(object_key: str):
    """
    Deletes a file from S3.

    Args:
        object_key: The S3 object key (path/filename).

    Raises:
        HTTPException: If the deletion fails.
    """
    if not S3_BUCKET_NAME:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3_BUCKET_NAME is not configured.")

    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=object_key)
    except ClientError as e:
        print(f"S3 deletion failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete file from S3: {e}")