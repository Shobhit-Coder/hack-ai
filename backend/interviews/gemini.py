import os
import json
import re
import asyncio
import logging

import google.generativeai as genai

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set; interview scoring is disabled.")

SYSTEM_PROMPT = """
You are an expert technical interviewer. Evaluate the quality of the candidate’s answers against the role.
Always reply with JSON: {"score": <0-100 float>, "rationale": "<<=3 concise sentences>"}.
"""

async def score_interview_responses(prompt: str) -> dict:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _invoke_model, prompt.strip())

def _invoke_model(prompt: str) -> dict:
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(f"{SYSTEM_PROMPT.strip()}\n\n{prompt}")
    text = getattr(response, "text", "") or _extract_text_from_candidates(response)
    if not text:
        raise ValueError("Gemini returned an empty response.")
    return _parse_json_payload(text)

def _extract_text_from_candidates(response) -> str:
    if not getattr(response, "candidates", None):
        return ""
    for candidate in response.candidates:
        for part in getattr(candidate.content, "parts", []):
            if getattr(part, "text", None):
                return part.text
    return ""

def _parse_json_payload(text: str) -> dict:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        payload = json.loads(match.group(0))
    score = float(payload.get("score", 0.0))
    return {
        "score": max(0.0, min(100.0, score)),
        "rationale": payload.get("rationale", "").strip()
    }
