import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER")
BLOB_PREFIX = os.getenv("AZURE_BLOB_PREFIX", "resumes/")   # default to resumes/
LOCAL_DOWNLOAD_PATH = os.getenv("LOCAL_RESUME_DIR", "/app/resumes")


def download_resumes_from_blob():
    """
    Downloads only blobs inside the `resumes/` folder.
    """

    if not CONNECTION_STRING:
        raise ValueError("ERROR: Missing AZURE_BLOB_CONNECTION_STRING in .env")

    if not CONTAINER_NAME:
        raise ValueError("ERROR: Missing AZURE_BLOB_CONTAINER in .env")

    os.makedirs(LOCAL_DOWNLOAD_PATH, exist_ok=True)

    print(f"[BLOB] Connecting to Azure Blob Storage...")
    blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service.get_container_client(CONTAINER_NAME)

    print(f"[BLOB] Listing blobs inside prefix '{BLOB_PREFIX}' ...")

    count = 0
    for blob in container_client.list_blobs(name_starts_with=BLOB_PREFIX):

        # Remove 'resumes/' prefix → keep only filename
        filename = blob.name.replace(BLOB_PREFIX, "")
        local_path = os.path.join(LOCAL_DOWNLOAD_PATH, filename)

        print(f"[BLOB] Downloading → {blob.name}")

        with open(local_path, "wb") as file:
            file.write(container_client.download_blob(blob).readall())

        count += 1

    print(f"[BLOB] Download complete: {count} file(s) downloaded from {BLOB_PREFIX}")
    return count
