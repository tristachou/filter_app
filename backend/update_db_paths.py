
import os
import json
import shutil

# This script updates the filter paths in your db.json to point to the new S3 locations.

def update_database_paths():
    """
    Reads the db.json file, backs it up, and updates the storage_path for each
    filter from a local path to an S3 key.
    """
    # 1. Define paths
    # The script is in /backend, and db.json is also in /backend
    db_path = os.path.join(os.path.dirname(__file__), "db.json")
    backup_path = f"{db_path}.bak"

    if not os.path.exists(db_path):
        print(f"\033[91mError: Database file not found at {db_path}\033[0m")
        print("Please ensure you are running this script from the 'backend' directory.")
        return

    # 2. Back up the database file
    try:
        shutil.copyfile(db_path, backup_path)
        print(f"Successfully created a backup of your database at: {backup_path}")
    except Exception as e:
        print(f"\033[91mError: Could not create backup file. Aborting. {e}\033[0m")
        return

    # 3. Load the database
    try:
        with open(db_path, 'r') as f:
            db_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\033[91mError: Could not parse {db_path}. It might be corrupted. {e}\033[0m")
        print(f"A backup has been created at {backup_path}. You may need to restore it manually.")
        return

    # 4. Update the filter paths
    filters_updated = 0
    filter_items = db_data.get("filter_items")
    if not filter_items:
        print("\033[93mWarning: No 'filter_items' found in the database. Nothing to update.\033[0m")
        return

    print("Scanning filter items for paths to update...")
    for filter_id, filter_item in filter_items.items():
        storage_path = filter_item.get("storage_path")
        if storage_path and storage_path.startswith("assets/luts/"):
            original_path = storage_path
            file_name = os.path.basename(storage_path)
            new_path = f"filters/{file_name}"
            
            # Update the value in the dictionary
            filter_item["storage_path"] = new_path
            filters_updated += 1
            print(f"  - Updating filter '{filter_item.get('name')}':")
            print(f"    \033[91mFrom:\t{original_path}\033[0m")
            print(f"    \033[92mTo:\t{new_path}\033[0m")

    if filters_updated == 0:
        print("No filter paths needed updating. Your database seems to be up to date.")
    else:
        # 5. Save the updated database
        try:
            with open(db_path, 'w') as f:
                json.dump(db_data, f, indent=4, default=str)
            print(f"\nSuccessfully updated {filters_updated} filter path(s) in {db_path}.")
        except Exception as e:
            print(f"\033[91mError: Failed to write updates to {db_path}. {e}\033[0m")
            print("Your original database is backed up.")

if __name__ == "__main__":
    update_database_paths()
