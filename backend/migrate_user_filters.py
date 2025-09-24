
import os
import json
import shutil
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# This is a one-time script to migrate existing user-uploaded filters
# from the old S3 path format (filters/{userid}/...)
# to the new format (filters/user/{userid}/...).

def migrate_user_filters():
    """
    Scans the database for custom filters with old path structures,
    moves the corresponding files on S3, and updates the database paths.
    """
    # 1. Define paths and get S3 bucket name
    db_path = os.path.join(os.path.dirname(__file__), "db.json")
    backup_path = f"{db_path}.mig-bak"
    s3_bucket_name = 'n11696630'

    if not s3_bucket_name:
        print("\033[91mError: S3_BUCKET_NAME environment variable is not set.\033[0m")
        return

    if not os.path.exists(db_path):
        print(f"\033[91mError: Database file not found at {db_path}\033[0m")
        return

    # 2. Back up the database file
    try:
        shutil.copyfile(db_path, backup_path)
        print(f"Successfully created a backup of your database at: {backup_path}")
    except Exception as e:
        print(f"\033[91mError: Could not create backup file. Aborting. {e}\033[0m")
        return

    # 3. Load the database
    with open(db_path, 'r') as f:
        db_data = json.load(f)

    # 4. Initialize Boto3 S3 client
    try:
        s3_client = boto3.client("s3")
        s3_client.head_bucket(Bucket=s3_bucket_name)
        print(f"Successfully connected to S3 bucket: {s3_bucket_name}")
    except (ClientError, NoCredentialsError) as e:
        print(f"\033[91mError connecting to S3: {e}. Please check your credentials and bucket name.\033[0m")
        return

    # 5. Find filters that need migration
    filters_to_migrate = []
    for filter_id, f in db_data.get("filter_items", {}).items():
        path = f.get("storage_path", "")
        # Target condition: custom filter AND path starts with 'filters/' but NOT 'filters/user/'
        if f.get("filter_type") == "custom" and path.startswith("filters/") and not path.startswith("filters/user/"):
            # Add the original dictionary object to the list to modify it directly
            filters_to_migrate.append(f)

    if not filters_to_migrate:
        print("\nNo user-uploaded filters with the old path structure found. Nothing to migrate.")
        return

    print(f"\nFound {len(filters_to_migrate)} user-uploaded filters to migrate.")
    
    # 6. Process migration for each filter
    success_count = 0
    fail_count = 0
    for f in filters_to_migrate:
        old_path = f["storage_path"]
        owner_id = f.get("owner_id")
        
        if not owner_id:
            print(f"\033[93mSkipping filter '{f.get('name')}' because it has no owner_id.\033[0m")
            continue

        file_name = os.path.basename(old_path)
        new_path = f"filters/user/{owner_id}/{file_name}"

        print(f"---\nMigrating filter: '{f.get('name')}'")
        print(f"  Old S3 key: {old_path}")
        print(f"  New S3 key: {new_path}")

        try:
            # A. Copy object to new location
            copy_source = {'Bucket': s3_bucket_name, 'Key': old_path}
            s3_client.copy_object(Bucket=s3_bucket_name, CopySource=copy_source, Key=new_path)
            print("  \033[92mStep 1/3: Copied to new S3 location successfully.\033[0m")

            # B. Delete old object
            s3_client.delete_object(Bucket=s3_bucket_name, Key=old_path)
            print("  \033[92mStep 2/3: Deleted old S3 object successfully.\033[0m")

            # C. Update path in database object
            f["storage_path"] = new_path
            success_count += 1
            print("  \033[92mStep 3/3: Database path marked for update.\033[0m")

        except ClientError as e:
            fail_count += 1
            if e.response["Error"]["Code"] == "NoSuchKey":
                print(f"  \033[91mError: S3 object not found at old path '{old_path}'. Cannot migrate. Updating DB path anyway to prevent future errors.\033[0m")
                # Still update the DB path to prevent the script from picking it up again
                f["storage_path"] = new_path
            else:
                print(f"  \033[91mAn unexpected S3 error occurred: {e}. Skipping this filter.\033[0m")

    # 7. Save the updated database
    if success_count > 0 or (fail_count > 0 and any(f.get("storage_path", "").startswith("filters/user/") for f in filters_to_migrate)):
        try:
            with open(db_path, 'w') as f:
                json.dump(db_data, f, indent=4, default=str)
            print(f"\n---\nDatabase file '{db_path}' has been updated.")
        except Exception as e:
            print(f"\n\033[91mCRITICAL ERROR: Failed to write final updates to {db_path}. {e}\033[0m")
            print(f"Your S3 files may be in an inconsistent state. Please restore the DB from {backup_path} and investigate.")
    
    print(f"\nMigration process complete. {success_count} successful, {fail_count} failed.")

if __name__ == "__main__":
    migrate_user_filters()
