import os
import json
import asyncio
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
# PROMPT: Extraction & Binary Fit Score
# -----------------------------------------------------
SYSTEM_INSTRUCTIONS_PARSE = """
You are an expert AI Recruiter. 
1. Parse the resume information into structured JSON.
2. Compare the resume against the provided JOB DESCRIPTION to make a strict Hiring Decision (0 or 1).

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
  "fit_score": integer, 
  "summary": string,
  "experience": [...], 
  "education": [...]
}

RULES:
- Split the full name into 'first_name' and 'last_name'.
- 'fit_score': STRICTLY 0 or 1.
- Validate: If email/phone is missing, try to find it.
- Return PURE JSON. No markdown.
"""

# -----------------------------------------------------
# PROMPT: Question Generation (UPDATED SCHEMA)
# -----------------------------------------------------
SYSTEM_INSTRUCTIONS_QUESTIONS = """
You are a Senior Technical Interviewer. 
Based on the Candidate's Resume and the Job Description below, generate exactly 5 interview questions.

JOB DESCRIPTION:
{job_description}

CANDIDATE SUMMARY:
{candidate_summary}

REQUIREMENTS:
- Generate exactly 5 questions.
- 'question_type' must be: 'Technical', 'Behavioral', or 'Experience'.
- 'sequence_number': 1 to 5.

OUTPUT SCHEMA (JSON ONLY):
{
  "interview_questions": [
    {
      "sequence_number": integer,
      "question_type": "string",
      "question": "string",
      "context": "Reason for asking"
    }
  ]
}
"""

# -----------------------------------------------------
# Helper Functions
# -----------------------------------------------------

def extract_resume_id(filename: str) -> str:
    base = os.path.basename(filename)
    return os.path.splitext(base)[0]

def log_failure(resume_id: str, filename: str, error: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(FAILED_LOG, "a", encoding="utf-8") as f:
        f.write(f"{resume_id} | {filename} | {error}\n")

def extract_json(text: str) -> str:
    text = text.replace("```json", "").replace("```", "")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No valid JSON found")
    return text[start:end+1]

def fetch_job_details(resume_id: str):
    url = f"{NGROK}/api/job-mapping/{resume_id}"
    print(f"[PARSER] Fetching JD for Resume ID: {resume_id}")
    try:
        # Mocking for now - Uncomment real request when ready
        # res = requests.get(url); data = res.json()
        data = {
            "job_id": "b3f1b2c3-9e4f-4e8a-a09a-123456789abc",
            "job_description": "Looking for a Python Developer with Azure Blob Storage, AsyncIO, and LLM integration experience."
        }
        return data.get("job_id"), data.get("job_description")
    except Exception as e:
        print(f"[PARSER] Failed to fetch JD: {e}")
        return None, None

def validate_parsed_data(data: dict) -> bool:
    required = ["first_name", "last_name", "email", "phone_number"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        print(f"[PARSER] Validation Failed. Missing: {missing}")
        return False
    return True

# -----------------------------------------------------
# Async Tasks
# -----------------------------------------------------

async def post_candidate_data(payload: dict, resume_id: str):
    """Task 1: Posts candidate info -> Returns new candidate_id"""
    url = f"{NGROK}/api/candidates"
    print(f"[ASYNC-1] Posting Profile {resume_id}...")
    try:
        res = await asyncio.to_thread(requests.post, url, json=payload, timeout=20)
        if res.status_code >= 400:
            print(f"[ASYNC-1] ❌ Error: {res.text}")
            return None
        
        data = res.json()
        # Capture the ID from response
        new_id = data.get("id") or data.get("candidate_id") or data.get("_id")
        print(f"[ASYNC-1] ✅ Created Candidate ID: {new_id}")
        return new_id
    except Exception as e:
        print(f"[ASYNC-1] ❌ Failed: {e}")
        return None

async def update_fit_score(fit_score: int, resume_id: str):
    """Task 2: Patches fit score"""
    url = f"{NGROK}/api/candidates/resume/{resume_id}"
    try:
        await asyncio.to_thread(requests.patch, url, json={"fit_score": fit_score}, timeout=20)
        print(f"[ASYNC-2] ✅ Score Updated")
    except Exception as e:
        print(f"[ASYNC-2] ❌ Failed: {e}")

async def generate_questions(parsed_data: dict, job_description: str):
    """Task 3: Generates questions via LLM -> Returns list of questions"""
    print(f"[ASYNC-3] Generating Questions...")
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    summary = json.dumps({
        "skills": parsed_data.get("skills"),
        "summary": parsed_data.get("summary")
    })
    prompt = SYSTEM_INSTRUCTIONS_QUESTIONS.format(job_description=job_description, candidate_summary=summary)

    try:
        response = await model.generate_content_async(prompt)
        data = json.loads(extract_json(response.text))
        questions = data.get("interview_questions", [])
        print(f"[ASYNC-3] ✅ Generated {len(questions)} questions")
        return questions
    except Exception as e:
        print(f"[ASYNC-3] ❌ Failed: {e}")
        return []

async def post_interview_questions(candidate_id: str, questions: list):
    """
    Task 4: Posts the generated questions to the new API.
    Dependency: Needs candidate_id (Task 1) and questions (Task 3).
    """
    url = f"{NGROK}/api/interviews/questions"
    
    # Construct payload - assuming API accepts a list or wrapper
    payload = {
        "candidate_id": candidate_id,
        "questions": questions
    }

    print(f"[ASYNC-4] Posting {len(questions)} questions for Candidate {candidate_id}...")
    
    try:
        res = await asyncio.to_thread(requests.post, url, json=payload, timeout=20)
        if res.status_code >= 400:
             print(f"[ASYNC-4] ❌ Backend Error: {res.text}")
        else:
             print(f"[ASYNC-4] ✅ Questions Posted Successfully")
    except Exception as e:
        print(f"[ASYNC-4] ❌ Connection Failed: {e}")

# -----------------------------------------------------
# MAIN PARSER CONTROLLER
# -----------------------------------------------------

async def parse_resume_async(filepath: str):
    print("--------------------------------------------------")
    print(f"[PARSER] Processing: {filepath}")

    resume_id = extract_resume_id(filepath)
    
    # 1. Fetch Context
    job_id, job_description = fetch_job_details(resume_id)
    if not job_id: return None

    # 2. Parse Resume (LLM Call 1)
    print("[PARSER] Step 1: Parsing Resume...")
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        uploaded_file = genai.upload_file(filepath)
        prompt = SYSTEM_INSTRUCTIONS_PARSE.format(job_description=job_description)
        
        response = await model.generate_content_async([prompt, uploaded_file])
        parsed_data = json.loads(extract_json(response.text))
        
        fit_score = int(parsed_data.get("fit_score", 0))
        # Force binary
        if fit_score not in [0, 1]: fit_score = 1 if fit_score > 0.5 else 0

    except Exception as e:
        log_failure(resume_id, filepath, f"Parse Error: {e}")
        return None

    if not validate_parsed_data(parsed_data): return None

    profile_payload = {
        "first_name": parsed_data.get("first_name"),
        "last_name": parsed_data.get("last_name"),
        "email": parsed_data.get("email"),
        "phone_number": parsed_data.get("phone_number"),
        "applied_job": job_id
    }

    # 3. Execute Parallel Tasks (Phase 1)
    print("[PARSER] Step 2: Executing Phase 1 (Create Profile, Update Score, Gen Questions)...")
    
    results = await asyncio.gather(
        post_candidate_data(profile_payload, resume_id),  # results[0] -> candidate_id
        update_fit_score(fit_score, resume_id),           # results[1] -> void
        generate_questions(parsed_data, job_description)  # results[2] -> questions list
    )

    new_candidate_id = results[0]
    generated_questions = results[2]

    # 4. Execute Dependent Task (Phase 2)
    # We can only post questions if we successfully got an ID and have questions
    if new_candidate_id and generated_questions:
        print("[PARSER] Step 3: Executing Phase 2 (Post Questions to Backend)...")
        await post_interview_questions(new_candidate_id, generated_questions)
    else:
        print("[PARSER] ⚠️ Skipping Question Post (Missing ID or Questions)")

    final_output = {
        "candidate_id": new_candidate_id,
        "fit_score": fit_score,
        "questions_count": len(generated_questions)
    }
    
    print(f"[PARSER] Process Complete for {resume_id}")
    return final_output

def parse_resume_file(filepath: str):
    return asyncio.run(parse_resume_async(filepath))