import os
import json
import requests
import google.generativeai as genai

# Load Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
from constants import NGROK
OUTPUT_DIR = "/app/output"
FAILED_LOG = os.path.join(OUTPUT_DIR, "failed_logs.txt")

SYSTEM_INSTRUCTIONS = """
You are an AI specialized in parsing resumes.

Extract ONLY the following fields and return VALID JSON:

{
  "name": string or null,
  "email": string or null,
  "phone": string or null,
  "skills": [string, ...], 
  "summary": string or null,
  "experience": [
    {
      "company": string or null,
      "title": string or null,
      "start_date": string or null,
      "end_date": string or null,
      "description": string or null
    }
  ],
  "education": [
    {
      "degree": string or null,
      "field": string or null,
      "institution": string or null,
      "start_year": string or null,
      "end_year": string or null
    }
  ]
}

STRICT RULES:
- 'skills' must contain ONLY real skills.
- Do NOT include headings, hobbies, languages, dates, responsibilities.
- Do NOT include duplicates.
- Remove any noisy or irrelevant items.
- Always return a single JSON object without explanation text.
"""

# -----------------------------------------------------
# Helper functions
# -----------------------------------------------------

def extract_resume_id(filename: str) -> str:
    """Extract the UUID before the first underscore."""
    base = os.path.basename(filename)
    id_number = base.split("_")[0]
    print(id_number)
    return id_number


def log_failure(resume_id: str, filename: str, error: str):
    """Write failure log."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(FAILED_LOG, "a", encoding="utf-8") as f:
        f.write(f"{resume_id} | {filename} | {error}\n")
    print(f"[PARSER][LOG] Logged failure for {resume_id}")


def extract_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No valid JSON found in model output")
    return text[start:end+1]


def clean_skills(skills):
    cleaned = []
    for s in skills:
        if not s or len(s) > 40:
            continue
        if "," in s:
            continue
        if s.lower() in ["skills", "languages", "hobbies", "achievements"]:
            continue
        if s not in cleaned:
            cleaned.append(s)
    return cleaned

# -----------------------------------------------------
# MAIN PARSER
# -----------------------------------------------------

def parse_resume_file(filepath: str) -> dict:
    print("--------------------------------------------------")
    print(f"[PARSER] Parsing file: {filepath}")

    resume_id = extract_resume_id(filepath)
    print(f"[PARSER] Resume ID: {resume_id}")

    backend_url = f"{NGROK}/api/candidates/resumes/{resume_id}"
    print(f"[PARSER] Backend URL: {backend_url}")

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Upload file to Gemini
    try:
        uploaded_file = genai.upload_file(filepath)
        print(f"[PARSER] File uploaded to Gemini: {uploaded_file.uri}")
    except Exception as e:
        error = f"Upload failed: {e}"
        print("[PARSER][ERROR]", error)
        log_failure(resume_id, filepath, error)
        return None

    # Generate LLM output
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([SYSTEM_INSTRUCTIONS, uploaded_file])
        print("[PARSER] Gemini response received.")
    except Exception as e:
        error = f"LLM model error: {e}"
        print("[PARSER][ERROR]", error)
        log_failure(resume_id, filepath, error)
        return None

    raw_output = response.text or ""

    # Extract JSON
    try:
        json_str = extract_json(raw_output)
        parsed = json.loads(json_str)
        print("[PARSER] JSON extraction success.")
    except Exception as e:
        error = f"JSON parse error: {e}"
        print("[PARSER][ERROR]", error)
        log_failure(resume_id, filepath, error)
        return None

    # Clean skills
    parsed["skills"] = clean_skills(parsed.get("skills", []))

    # Build final payload for backend
    payload = {
        "parsed_data": parsed
    }

    # PATCH to backend
    try:
        print("[PARSER] Sending parsed data to backend via PATCH...")
        res = requests.patch(backend_url, json=payload, timeout=20)

        print("[PARSER] Backend status:", res.status_code)
        print("[PARSER] Backend response:", res.text)

        if res.status_code >= 400:
            raise Exception(f"Backend returned {res.status_code}: {res.text}")

    except Exception as e:
        error = f"Backend PATCH failed: {e}"
        print("[PARSER][ERROR]", error)
        log_failure(resume_id, filepath, error)
        return None

