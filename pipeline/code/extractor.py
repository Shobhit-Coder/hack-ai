# extractor.py
import os
from dotenv import load_dotenv
from blob_utils import download_resumes_from_blob

load_dotenv()

RESUME_DIR = os.getenv("LOCAL_RESUME_DIR", "/app/resumes")


def extract_all_resumes() -> list:
    """
    Downloads resumes from Azure Blob and returns a list of filenames.
    No text extraction. Raw files only.
    """
    print("[EXTRACTOR] Downloading resumes from Azure Blob...")
    download_resumes_from_blob()

    if not os.path.exists(RESUME_DIR):
        print("[EXTRACTOR] Resume directory does not exist:", RESUME_DIR)
        return []

    files = [
        f for f in os.listdir(RESUME_DIR)
        if os.path.isfile(os.path.join(RESUME_DIR, f))
        and f.lower().endswith((".pdf", ".docx", ".txt"))
    ]

    print("[EXTRACTOR] Downloaded files:", files)
    return files
