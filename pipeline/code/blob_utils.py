import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER")
BLOB_PREFIX = os.getenv("AZURE_BLOB_PREFIX", "resumes/")
LOCAL_DOWNLOAD_PATH = os.getenv("LOCAL_RESUME_DIR", "/app/resumes")

def download_resumes_from_blob():
    """
    Downloads blobs inside the `resumes/` folder.
    Maintains folder structure locally and skips existing files.
    """

    if not CONNECTION_STRING:
        raise ValueError("ERROR: Missing AZURE_BLOB_CONNECTION_STRING in .env")

    if not CONTAINER_NAME:
        raise ValueError("ERROR: Missing AZURE_BLOB_CONTAINER in .env")

    # Ensure base directory exists
    os.makedirs(LOCAL_DOWNLOAD_PATH, exist_ok=True)

    print(f"[BLOB] Connecting to Azure Blob Storage...")
    try:
        blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container_client = blob_service.get_container_client(CONTAINER_NAME)
    except Exception as e:
        print(f"[BLOB] Connection failed: {e}")
        return 0

    print(f"[BLOB] Listing blobs inside prefix '{BLOB_PREFIX}' ...")

    count = 0
    blobs = container_client.list_blobs(name_starts_with=BLOB_PREFIX)

    for blob in blobs:
        # 1. Handle Folder Blobs (Azure sometimes lists empty folders as blobs)
        if blob.name.endswith('/'):
            continue

        # 2. Construct Local Path
        # Remove prefix safely to get relative path (e.g., "subfolder/resume.pdf")
        relative_path = blob.name[len(BLOB_PREFIX):] if blob.name.startswith(BLOB_PREFIX) else blob.name
        # Remove leading slashes if any remain
        relative_path = relative_path.lstrip('/')
        
        local_path = os.path.join(LOCAL_DOWNLOAD_PATH, relative_path)

        # 3. Ensure local subdirectories exist
        local_dir = os.path.dirname(local_path)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        # 4. Skip if file exists (Incremental Download)
        if os.path.exists(local_path):
            # Optional: You could compare blob.size with local file size to check for updates
            print(f"[BLOB] Skipping existing -> {relative_path}")
            continue

        print(f"[BLOB] Downloading -> {relative_path}")
        
        try:
            with open(local_path, "wb") as file:
                file.write(container_client.download_blob(blob).readall())
            count += 1
        except Exception as e:
            print(f"[ERROR] Failed to download {blob.name}: {e}")

    print(f"[BLOB] Download complete: {count} new file(s).")
    return count