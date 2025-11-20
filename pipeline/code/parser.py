# parser.py
import os
import json
import asyncio
import requests
import traceback
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()

from constants import NGROK

# -----------------------------
# Global config
# -----------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

BASE_URL = NGROK.rstrip("/")  # centralize base URL

OUTPUT_DIR = "/app/output"
FAILED_LOG = os.path.join(OUTPUT_DIR, "failed_logs.txt")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------
# 🛡️ SAFETY SETTINGS
# -----------------------------------------------------
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# -----------------------------------------------------
# ⚙️ GENERATION CONFIG (FORCE JSON)
# -----------------------------------------------------
JSON_CONFIG = {
    "response_mime_type": "application/json",
    "temperature": 0.0,  # Deterministic output
}

# -----------------------------------------------------
# PROMPTS
# -----------------------------------------------------
SYSTEM_INSTRUCTIONS_PARSE = """
You are an expert AI Recruiter. 
Parse the resume information into structured JSON.

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this specific schema:
{
  "first_name": string or null,
  "last_name": string or null,
  "email": string or null,
  "phone_number": string or null,
  "skills": [string, ...],
  "summary": string or null,
  "experience": [...],
  "education": [...]
}

RULES:
- Split the full name into 'first_name' and 'last_name'.
- 'skills' should be a flat list of skill names (e.g. ["Python", "Azure", "Kubernetes"]).
- 'experience' can be an array of objects or strings, but must be JSON-serializable.
- Validate: If email/phone is missing, try to find it in the resume.
- Do NOT include any scoring or fit fields.
"""

# IMPORTANT: all literal JSON braces are escaped as {{ }} so .format() doesn't treat them as placeholders
SYSTEM_INSTRUCTIONS_QUESTIONS = """
You are a Senior Technical Interviewer. 
Based on the Candidate's Resume and the Job Description below, generate a set of interview questions.

JOB DESCRIPTION:
{job_description}

CANDIDATE DATA (JSON):
{candidate_json}

OUTPUT SCHEMA (JSON ONLY):
{{
  "interview_questions": [
    {{
      "sequence_number": integer,
      "question_type": "technical" | "behavioral" | "experience" | "other",
      "question": "string",
      "context": "Reason for asking"
    }}
  ]
}}

RULES:
- Generate between 10 questions.
- Mix technical and behavioral questions.
- Tailor questions to the candidate's skills and experience seniority.
"""


# -----------------------------------------------------
# Helper Functions
# -----------------------------------------------------

def extract_resume_id(filename: str) -> str:
    """Extracts resume_id from filename (without extension)."""
    base = os.path.basename(filename)
    return os.path.splitext(base)[0]


def log_failure(resume_id: str, filename: str, error: str):
    """Append failure information to a log file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(FAILED_LOG, "a", encoding="utf-8") as f:
        f.write(f"{resume_id} | {filename} | {error}\n")


def validate_parsed_data(data: dict) -> bool:
    """
    Validates minimum contact fields for candidate creation.
    Parsing itself is considered successful even if this fails.
    """
    required = ["first_name", "last_name", "email", "phone_number"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        print(f"[PARSER] Validation Failed. Missing: {missing}")
        return False
    return True


def compute_resume_job_score(parsed_data: dict, job_description: str) -> float:
    """
    Computes a simple numeric resume-job fit score in [0, 1]
    based on overlap between candidate skills and JD keywords.
    """
    skills = [s.lower() for s in (parsed_data.get("skills") or [])]
    jd_text = (job_description or "").lower()

    keyword_candidates = ["python", "azure", "blob", "asyncio", "llm", "sql", "docker", "kubernetes"]
    jd_keywords = [k for k in keyword_candidates if k in jd_text]

    if not jd_keywords:
        print("[PARSER] ⚠️ No JD keywords detected; defaulting resume_job_score to 0.0")
        return 0.0

    overlap = set(skills) & set(jd_keywords)
    coverage = len(overlap) / len(jd_keywords)

    score = round(coverage, 2)
    print(f"[PARSER] Skill overlap: {overlap} | coverage={coverage:.2f} -> score={score}")
    return score


def fetch_job_details(resume_id: str):
    """
    Fetches job_id and job_description from backend using resume_id.

    Assumption:
    - API endpoint: GET {BASE_URL}/api/candidates/resumes/<resume_id>/job-info
    - Response JSON shape (example):
      {
        "job_id": "uuid-here",
        "job_description": "Long JD text..."
      }
    """
    print(f"[PARSER] Fetching JD for Resume ID: {resume_id}")
    url = f"{BASE_URL}/api/candidates/resumes/{resume_id}/job-info"

    try:
        res = requests.get(url, timeout=20)
        if res.status_code >= 400:
            print(f"[PARSER] ❌ JD API error ({res.status_code}): {res.text}")
            return None, None

        data = res.json()
        job_id = data.get("job_id") or data.get("id")
        job_description = data.get("job_description") or data.get("description")

        if not job_id or not job_description:
            print("[PARSER] ❌ JD API response missing 'job_id' or 'job_description'")
            return None, None

        print(f"[PARSER] ✅ JD fetched. job_id={job_id}")
        return job_id, job_description

    except Exception as e:
        print(f"[PARSER] Failed to fetch JD: {e}")
        return None, None


async def wait_for_file_active(uploaded_file):
    """Waits for the uploaded file to be ready for processing (Gemini Files API)."""
    print(f"[PARSER] Waiting for file processing: {uploaded_file.name}...")
    while uploaded_file.state.name == "PROCESSING":
        await asyncio.sleep(2)
        uploaded_file = genai.get_file(uploaded_file.name)

    if uploaded_file.state.name != "ACTIVE":
        raise Exception(f"File upload failed with state: {uploaded_file.state.name}")

    print(f"[PARSER] File is ACTIVE and ready.")


# -----------------------------------------------------
# Async network helpers
# -----------------------------------------------------

async def patch_resume_job_score(resume_id: str, resume_job_score):
    """
    PATCH resume_job_score to backend:
    PATCH {BASE_URL}/api/candidates/resume/<resume_id>
    Payload: {"resume_job_score": <score or object>}
    """
    url = f"{BASE_URL}/api/candidates/resume/{resume_id}"
    payload = {"resume_job_score": resume_job_score}
    print(f"[PARSER] Patching resume_job_score for {resume_id} -> {resume_job_score}")
    try:
        res = await asyncio.to_thread(requests.patch, url, json=payload, timeout=20)
        if res.status_code >= 400:
            print(f"[PARSER] ❌ Error PATCHing resume_job_score: {res.status_code} {res.text}")
        else:
            print("[PARSER] ✅ resume_job_score patched successfully")
    except Exception as e:
        print(f"[PARSER] ❌ Exception while PATCHing resume_job_score: {e}")


async def post_candidate_data(profile_payload: dict, resume_id: str):
    """
    Creates candidate profile:
    POST {BASE_URL}/api/candidates
    Payload: profile_payload
    Returns candidate_id or None.
    """
    url = f"{BASE_URL}/api/candidates"
    print(f"[PARSER] Posting candidate profile for resume_id={resume_id}...")
    print(f"profile_payload {profile_payload}")
    try:
        res = await asyncio.to_thread(requests.post, url, json=profile_payload, timeout=20)
        if res.status_code >= 400:
            print(f"[PARSER] ❌ Error creating candidate: {res.status_code} {res.text}")
            return None

        data = res.json()
        candidate_id = data.get("candidate_id") or data.get("id") or data.get("_id")
        print(f"[PARSER] ✅ Created Candidate ID: {candidate_id}")
        return candidate_id
    except Exception as e:
        print(f"[PARSER] ❌ Exception while creating candidate: {e}")
        return None


async def generate_questions(parsed_data: dict, job_description: str):
    """
    Uses Gemini to generate interview questions based on:
    - parsed_data["skills"]
    - parsed_data["experience"]
    - job_description

    RETURN:
      List[dict] where each dict is:
        {
          "sequence_number": int,
          "question_type": str,
          "question_text": str,
        }

    Any parsing issue is handled locally; returns [] on failure.
    """
    print(f"[PARSER] Generating interview questions via LLM...")
    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=JSON_CONFIG)

    candidate_json = json.dumps(
        {
            "skills": parsed_data.get("skills"),
            "experience": parsed_data.get("experience"),
            "summary": parsed_data.get("summary"),
        },
        ensure_ascii=False,
    )

    # This .format was previously crashing because of unescaped braces in the template.
    prompt = SYSTEM_INSTRUCTIONS_QUESTIONS.format(
        job_description=job_description,
        candidate_json=candidate_json,
    )

    raw = None
    try:
        response = await model.generate_content_async(
            prompt,
            safety_settings=SAFETY_SETTINGS,
        )
        raw = response.text
        print("[PARSER][DEBUG] Raw LLM questions response:")
        print(raw)

        # Primary JSON parse
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[PARSER] ⚠️ JSON decode failed in questions: {e}")
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = raw[start:end + 1]
                print("[PARSER][DEBUG] Trying cleaned JSON substring for questions:")
                print(cleaned)
                data = json.loads(cleaned)
            else:
                print("[PARSER] ❌ Could not isolate JSON object in questions response.")
                return []

        if not isinstance(data, dict):
            print(f"[PARSER] ❌ Questions JSON top-level is not a dict. Got: {type(data)}")
            return []

        if "interview_questions" not in data:
            print(f"[PARSER] ❌ 'interview_questions' key missing in LLM JSON. Keys: {list(data.keys())}")
            return []

        questions_obj = data.get("interview_questions") or []
        if not isinstance(questions_obj, list):
            print(f"[PARSER] ❌ 'interview_questions' is not a list. Type: {type(questions_obj)}")
            return []

        question_dicts = []
        for idx, q in enumerate(questions_obj, start=1):
            if not isinstance(q, dict):
                print(f"[PARSER] ⚠️ Skipping non-dict question item at index {idx}: {q}")
                continue

            text = q.get("question")
            if not text:
                print(f"[PARSER] ⚠️ Skipping question with no 'question' field at index {idx}: {q}")
                continue

            q_type = q.get("question_type") or "general"
            seq = q.get("sequence_number") or idx
            try:
                seq = int(seq)
            except Exception:
                seq = idx

            question_dicts.append(
                {
                    "sequence_number": seq,
                    "question_type": str(q_type),
                    "question_text": str(text),
                }
            )

        print(f"[PARSER] ✅ Generated {len(question_dicts)} questions")
        return question_dicts

    except Exception as e:
        print(f"[PARSER] 🔥 ERROR Generating Questions: {e}")
        print("[PARSER][TRACEBACK] generate_questions exception:")
        print(traceback.format_exc())
        print("[PARSER][DEBUG] Raw LLM questions response (for debugging):")
        print(raw)
        return []


async def post_interview_questions(candidate_id: str, questions: list):
    """
    Stores generated interview questions.

    Backend contract (you provided):
      POST /api/interviews/candidates/<candidate_id>/questions
      Payload:
      {
        "question_text": "What is your experience with Python?",
        "question_type": "technical",
        "sequence_number": 1
      }

    Here we:
      - POST each question individually.
      - candidate_id is taken from the URL path, not payload.
    """
    base = f"{BASE_URL}/api/interviews/candidates/{candidate_id}/questions"

    print(f"[PARSER] Posting {len(questions)} questions for Candidate {candidate_id}...")

    for q in questions:
        if not isinstance(q, dict):
            print(f"[PARSER] ⚠️ Skipping non-dict question payload: {q}")
            continue

        question_text = q.get("question_text")
        question_type = q.get("question_type") or "general"
        sequence_number = q.get("sequence_number") or 1

        if not question_text:
            print(f"[PARSER] ⚠️ Skipping question with empty text: {q}")
            continue

        try:
            sequence_number = int(sequence_number)
        except Exception:
            sequence_number = 1

        payload = {
            "question_text": question_text,
            "question_type": question_type,
            "sequence_number": sequence_number,
        }

        print(f"[PARSER] -> POST {base} payload={payload}")
        try:
            res = await asyncio.to_thread(
                requests.post, base, json=payload, timeout=20
            )
            if res.status_code >= 400:
                print(
                    f"[PARSER] ❌ Backend Error posting question "
                    f"(seq={sequence_number}): {res.status_code} {res.text}"
                )
            else:
                print(
                    f"[PARSER] ✅ Question (seq={sequence_number}) posted successfully"
                )
        except Exception as e:
            print(
                f"[PARSER] ❌ Connection Failed while posting question "
                f"(seq={sequence_number}): {e}"
            )
            print("[PARSER][TRACEBACK] post_interview_questions exception:")
            print(traceback.format_exc())


# -----------------------------------------------------
# MAIN CONTROLLER: one full pass for a single resume
# -----------------------------------------------------

async def parse_resume_async(filepath: str):
    """
    Orchestrates the entire flow for a single resume file:

    1) Parse resume with LLM -> parsed_data.
    2) Fetch job description via API using resume_id.
    3) Compute resume_job_score and PATCH it to backend.
    4) Create candidate profile via POST /api/candidates.
    5) Generate interview questions with LLM.
    6) Store questions via POST /api/interviews/candidates/<candidate_id>/questions.
    """
    print("--------------------------------------------------")
    print(f"[PARSER] Processing: {filepath}")

    resume_id = extract_resume_id(filepath)

    # ----------------------
    # Step 1: Parse resume with LLM
    # ----------------------
    print("[PARSER] Step 1: Parsing Resume with LLM...")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash", generation_config=JSON_CONFIG)

        uploaded_file = genai.upload_file(filepath)
        await wait_for_file_active(uploaded_file)

        response = await model.generate_content_async(
            [SYSTEM_INSTRUCTIONS_PARSE, uploaded_file],
            safety_settings=SAFETY_SETTINGS,
        )

        raw = response.text
        print("[PARSER][DEBUG] Raw LLM parse response:")
        print(raw)

        parsed_data = json.loads(raw)

    except Exception as e:
        print(f"🔥🔥🔥 [CRITICAL ERROR] LLM parse failed for {resume_id}: {e}")
        print("[PARSER][TRACEBACK] parse_resume_async (parse step) exception:")
        print(traceback.format_exc())
        log_failure(resume_id, filepath, f"Parse Error: {e}")
        return None

    has_valid_contact = validate_parsed_data(parsed_data)

    # ----------------------
    # Step 2: Fetch job description via API
    # ----------------------
    print("[PARSER] Step 2: Fetching Job Description from backend...")
    job_id, job_description = fetch_job_details(resume_id)
    if not job_id or not job_description:
        print(f"[PARSER] ❌ No JD for resume_id={resume_id}. Skipping scoring and candidate creation.")
        log_failure(resume_id, filepath, "Missing job description from API")
        return {
            "candidate_id": None,
            "resume_job_score": None,
            "questions_count": 0,
        }

    # ----------------------
    # Step 3: Compute fit score (resume_job_score) and PATCH it
    # ----------------------
    print("[PARSER] Step 3: Computing resume_job_score...")
    resume_job_score = compute_resume_job_score(parsed_data, job_description)
    await patch_resume_job_score(resume_id, resume_job_score)

    # ----------------------
    # Step 4: Create candidate profile
    # ----------------------
    candidate_id = None
    questions = []

    if has_valid_contact:
        print("[PARSER] Step 4: Creating candidate profile...")
        profile_payload = {
            "first_name": parsed_data.get("first_name"),
            "last_name": parsed_data.get("last_name"),
            "email": parsed_data.get("email"),
            "phone_number": parsed_data.get("phone_number"),
            "applied_job": job_id,
        }

        candidate_id = await post_candidate_data(profile_payload, resume_id)
    else:
        print("[PARSER] ⚠️ Missing contact fields; skipping candidate creation.")

    # ----------------------
    # Step 5: Generate and store interview questions
    # ----------------------
    if candidate_id:
        print("[PARSER] Step 5: Generating interview questions...")
        try:
            questions = await generate_questions(parsed_data, job_description)
            print(f"[PARSER] Step 5: generate_questions returned {len(questions)} items")

            if questions:
                await post_interview_questions(candidate_id, questions)
            else:
                print("[PARSER] ⚠️ No questions generated; skipping question POST.")
        except Exception as e:
            print(f"[PARSER] 🔥 ERROR in Step 5 (questions pipeline) for {resume_id}: {e}")
            print("[PARSER][TRACEBACK] Step 5 exception:")
            print(traceback.format_exc())
            questions = []
    else:
        print("[PARSER] ⚠️ No candidate_id; skipping questions generation and storage.")

    final_output = {
        "candidate_id": candidate_id,
        "resume_job_score": resume_job_score,
        "questions_count": len(questions),
    }

    print(f"[PARSER] Process Complete for {resume_id} -> {final_output}")
    return final_output


def parse_resume_file(filepath: str):
    """
    Public sync wrapper used by Airflow.
    Do NOT change this signature.
    """
    return asyncio.run(parse_resume_async(filepath))
