
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# This script uploads LUT files from the local assets/luts directory to your S3 bucket.

def upload_luts_to_s3():
    """
    Finds all .CUBE files in the local assets/luts directory and uploads them
    to a 'filters/' directory in the configured S3 bucket.
    """
    # 1. Get S3 Bucket Name from environment variable
    s3_bucket_name = 'n11696630'
    if not s3_bucket_name:
        print("\033[91mError: S3_BUCKET_NAME environment variable is not set.\033[0m")
        print("Please set it before running this script (e.g., in your .env file).")
        return

    # 2. Define local and remote paths
    # The script is in /backend, so assets/luts is relative to the current dir
    local_luts_dir = os.path.join(os.path.dirname(__file__), "assets", "luts")
    s3_prefix = "filters/"

    if not os.path.isdir(local_luts_dir):
        print(f"\033[91mError: Local LUTs directory not found at {local_luts_dir}\033[0m")
        return

    # 3. Initialize Boto3 S3 client
    try:
        s3_client = boto3.client("s3")
        # Verify bucket exists and we have access
        s3_client.head_bucket(Bucket=s3_bucket_name)
        print(f"Successfully connected to S3 bucket: {s3_bucket_name}")
    except NoCredentialsError:
        print("\033[91mError: AWS credentials not found.\033[0m")
        print("Please configure your credentials (e.g., run 'aws sso login').")
        return
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print(f"\033[91mError: Bucket '{s3_bucket_name}' not found.\033[0m")
        else:
            print(f"\033[91mAn error occurred connecting to S3: {e}\033[0m")
        return

    # 4. List local LUT files
    lut_files = [f for f in os.listdir(local_luts_dir) if f.upper().endswith((".CUBE", ".CUBE"))]
    if not lut_files:
        print(f"No .CUBE files found in {local_luts_dir}.")
        return

    print(f"Found {len(lut_files)} LUT files to potentially upload.")

    # 5. Iterate and upload
    for file_name in lut_files:
        local_file_path = os.path.join(local_luts_dir, file_name)
        s3_key = f"{s3_prefix}{file_name}"

        try:
            # Check if file already exists in S3
            s3_client.head_object(Bucket=s3_bucket_name, Key=s3_key)
            print(f"\033[93mSkipping '{file_name}', already exists in S3 as '{s3_key}'.\033[0m")
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                # File does not exist, so we can upload it
                print(f"Uploading '{file_name}' to S3 as '{s3_key}'...", end="")
                try:
                    s3_client.upload_file(local_file_path, s3_bucket_name, s3_key, ExtraArgs={'ContentType': 'application/octet-stream'})
                    print("\033[92m Success!\033[0m")
                except Exception as upload_error:
                    print(f"\033[91m Failed: {upload_error}\033[0m")
            else:
                # Some other error occurred
                print(f"\033[91mAn error occurred checking '{file_name}' in S3: {e}\033[0m")

    print("\nLUT upload process complete.")

if __name__ == "__main__":
    upload_luts_to_s3()
