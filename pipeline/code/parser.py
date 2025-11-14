import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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


def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No valid JSON found in model output")
    return text[start:end+1]


def parse_resume_file(filepath: str) -> dict:
    print("--------------------------------------------------")
    print(f"[PARSER] Starting parse for file: {filepath}")

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    print(f"[PARSER] Using Gemini model: {model_name}")

    # Upload file
    try:
        print(f"[PARSER] Uploading file to Gemini: {filepath}")
        uploaded_file = genai.upload_file(filepath)
        print(f"[PARSER] Upload successful: {uploaded_file.uri}")
    except Exception as e:
        print(f"[PARSER][ERROR] Upload failed for {filepath}: {e}")
        raise

    # Generate content
    try:
        print(f"[PARSER] Sending request to Gemini model...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([SYSTEM_INSTRUCTIONS, uploaded_file])
        print("[PARSER] Gemini response received.")
    except Exception as e:
        print(f"[PARSER][ERROR] Gemini model error for {filepath}: {e}")
        raise

    # Extract text response
    output = response.text or ""
    print(f"[PARSER] Raw model output length: {len(output)}")

    # Extract JSON
    try:
        print("[PARSER] Extracting JSON from model output...")
        json_str = extract_json(output)
        print(f"[PARSER] JSON extraction successful. Length: {len(json_str)}")
        data = json.loads(json_str)
        print("[PARSER] JSON parsed successfully.")
    except Exception as e:
        print(f"[PARSER][ERROR] Failed to extract valid JSON for {filepath}: {e}")
        print(f"[PARSER][DEBUG] Model output (first 500 chars): {output[:500]}")
        raise

    # Clean skills
    try:
        print("[PARSER] Cleaning skills list...")
        data["skills"] = clean_skills(data.get("skills", []))
        print("[PARSER] Skills cleaned.")
    except Exception as e:
        print(f"[PARSER][ERROR] Skills cleanup failed: {e}")
        raise

    # Add trace file
    data["file"] = filepath

    print("[PARSER] Finished parsing file successfully.")
    print("--------------------------------------------------")

    return data
