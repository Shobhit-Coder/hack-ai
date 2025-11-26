# azure_storage_utils.py (You might put this in a separate utility file)
import os
from azure.storage.blob import BlobServiceClient
from django.core.files.uploadedfile import UploadedFile

def upload_file_to_azure_blob(file_obj: UploadedFile, container_name: str, blob_name: str) -> str:
    """
    Uploads a Django UploadedFile object to Azure Blob Storage.

    Args:
        file_obj: The Django UploadedFile instance (e.g., request.data['file']).
        container_name: The name of the Azure Blob container.
        blob_name: The desired name for the file in the blob storage.

    Returns:
        The full URL of the uploaded blob.
    """
    try:
        # Get connection string from environment variable
        connection_string = os.getenv("BLOB_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("BLOB_CONNECTION_STRING environment variable not set.")
            
        # Create the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get a client for the specific blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Rewind the file stream to the beginning before uploading
        file_obj.seek(0)

        blob_client.upload_blob(
            file_obj.file, 
            blob_type="BlockBlob", 
            overwrite=True
        )

        return blob_client.url

    except Exception as ex:
        print(f"Azure Blob Upload Error: {ex}")
        raise

