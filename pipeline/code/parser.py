# parser.py
import os
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from constants import NGROK

OUTPUT_DIR = "/app/output"
FAILED_LOG = os.path.join(OUTPUT_DIR, "failed_logs.txt")

# -----------------------------------------------------
# SYSTEM PROMPT (Updated for Matching & Name Splitting)
# -----------------------------------------------------
SYSTEM_INSTRUCTIONS = """
You are an expert AI Recruiter. Your task is two-fold:
1. Parse the resume information into structured JSON.
2. Compare the resume against the provided JOB DESCRIPTION to calculate a fit score.

JOB DESCRIPTION:
{job_description}

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this specific schema:
{
  "first_name": string or null,
  "last_name": string or null,
  "email": string or null,
  "phone_number": string or null,
  "skills": [string, ...],
  "fit_score": float (0.0 to 1.0),
  "summary": string,
  "experience": [...], 
  "education": [...]
}

RULES:
- Split the full name into 'first_name' and 'last_name'.
- 'fit_score': Analyze how well the skills/experience match the Job Description. 0.0 is no match, 1.0 is perfect match.
- 'skills': Extract technical and soft skills. Remove noisy headers.
- Validate: If email or phone is missing, try to find it.
- Return PURE JSON. No markdown formatting.
"""

# -----------------------------------------------------
# Helper functions
# -----------------------------------------------------

def extract_resume_id(filename: str) -> str:
    """
    Returns the filename without extension.
    Ex: 'John_Doe_123.pdf' -> 'John_Doe_123'
    """
    base = os.path.basename(filename)
    resume_id = os.path.splitext(base)[0]
    return resume_id


def log_failure(resume_id: str, filename: str, error: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(FAILED_LOG, "a", encoding="utf-8") as f:
        f.write(f"{resume_id} | {filename} | {error}\n")


def extract_json(text: str) -> str:
    """Clean markdown JSON wrappers if present."""
    text = text.replace("```json", "").replace("```", "")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No valid JSON found")
    return text[start:end+1]


def fetch_job_details(resume_id: str):
    """
    Fetches the Job Description and Job ID associated with this resume.
    """
    # TODO: UPDATE THIS ENDPOINT URL
    # Assuming the API is: GET /api/job-mapping/{resume_id}
    url = f"{NGROK}/api/job-mapping/{resume_id}"
    
    print(f"[PARSER] Fetching JD for Resume ID: {resume_id} from {url}")
    
    try:
        # Mocking the call structure - Update with your actual API logic
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        
        # --- MOCK DATA FOR TESTING (DELETE THIS BLOCK WHEN API IS READY) ---
        # data = {
        #     "job_id": "b3f1b2c3-9e4f-4e8a-a09a-123456789abc",
        #     "job_description": "We need a Python Developer with Azure and LLM experience."
        # }
        # -------------------------------------------------------------------

        return data.get("job_id"), data.get("job_description")
    except Exception as e:
        print(f"[PARSER] Failed to fetch JD: {e}")
        return None, None


def validate_parsed_data(data: dict) -> bool:
    """
    Ensures critical fields are present.
    """
    required = ["first_name", "last_name", "email", "phone_number"]
    missing = [field for field in required if not data.get(field)]
    
    if missing:
        print(f"[PARSER] Validation Failed. Missing: {missing}")
        return False
    return True

# -----------------------------------------------------
# MAIN PARSER
# -----------------------------------------------------

def parse_resume_file(filepath: str) -> dict:
    print("--------------------------------------------------")
    print(f"[PARSER] Processing: {filepath}")

    # 1. Get ID
    resume_id = extract_resume_id(filepath)
    print(f"[PARSER] Resume ID: {resume_id}")

    # 2. Get Job Description & Job ID
    job_id, job_description = fetch_job_details(resume_id)
    
    if not job_id or not job_description:
        error = "Could not retrieve Job Description or Job ID."
        print(f"[PARSER][ERROR] {error}")
        log_failure(resume_id, filepath, error)
        return None

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash") # Use Flash for speed/cost

    # 3. Upload File to Gemini
    try:
        uploaded_file = genai.upload_file(filepath)
        print(f"[PARSER] File uploaded to Gemini: {uploaded_file.uri}")
    except Exception as e:
        log_failure(resume_id, filepath, f"Gemini Upload Failed: {e}")
        return None

    # 4. Inject JD into System Prompt and Generate
    try:
        formatted_prompt = SYSTEM_INSTRUCTIONS.format(job_description=job_description)
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([formatted_prompt, uploaded_file])
        
        raw_output = response.text
        parsed = json.loads(extract_json(raw_output))
        print(f"[PARSER] LLM Success. Fit Score: {parsed.get('fit_score')}")
        
    except Exception as e:
        log_failure(resume_id, filepath, f"LLM/JSON Error: {e}")
        return None

    # 5. Validate Data
    if not validate_parsed_data(parsed):
        log_failure(resume_id, filepath, "Validation Failed (Missing Name/Email/Phone)")
        return None

    # 6. Prepare Backend Payload
    candidate_payload = {
        "first_name": parsed.get("first_name"),
        "last_name": parsed.get("last_name"),
        "email": parsed.get("email"),
        "phone_number": parsed.get("phone_number"),
        "applied_job": job_id,
        # You can store the full parsed data + score elsewhere or add extra fields if your API supports it
        # "fit_score": parsed.get("fit_score"), 
        # "raw_skills": parsed.get("skills") 
    }

    # 7. POST to Backend
    backend_url = f"{NGROK}/api/candidates"
    
    try:
        print(f"[PARSER] Posting candidate to {backend_url}...")
        res = requests.post(backend_url, json=candidate_payload, timeout=20)

        print("[PARSER] Backend Status:", res.status_code)
        if res.status_code >= 400:
            raise Exception(f"Backend Error: {res.text}")
            
        print("[PARSER] Success!")
        return parsed

    except Exception as e:
        log_failure(resume_id, filepath, f"Backend POST Failed: {e}")
        return None