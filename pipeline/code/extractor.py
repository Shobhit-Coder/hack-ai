# extractor.py
import os
import fitz  # PyMuPDF
from docx import Document

from ocr import run_ocr_on_pdf  # <- use your ocr helper

RESUME_DIR = "/app/resumes"   # or "/app/input" if you change the mount
MIN_PYMUPDF_TEXT_LEN = 40     # threshold before we fallback to OCR


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""

    # 1) Try PyMuPDF
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()

        # If we got decent text, return it
        if len(text.strip()) > MIN_PYMUPDF_TEXT_LEN:
            return text
    except Exception as e:
        print(f"[WARN] PyMuPDF extraction failed for {pdf_path}: {e}")

    # 2) Fallback: OCR
    print(f"[INFO] Falling back to OCR for {pdf_path}")
    ocr_text = run_ocr_on_pdf(pdf_path)
    return ocr_text


def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_all_resumes() -> dict:
    """
    Returns: { filename: extracted_text }
    """
    results = {}

    if not os.path.exists(RESUME_DIR):
        print("Resume directory not found:", RESUME_DIR)
        return results

    for filename in os.listdir(RESUME_DIR):
        path = os.path.join(RESUME_DIR, filename)

        if filename.lower().endswith(".pdf"):
            results[filename] = extract_text_from_pdf(path)

        elif filename.lower().endswith(".docx"):
            results[filename] = extract_text_from_docx(path)

        elif filename.lower().endswith(".txt"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                results[filename] = f.read()

        else:
            print("Skipping unsupported file:", filename)

    return results
