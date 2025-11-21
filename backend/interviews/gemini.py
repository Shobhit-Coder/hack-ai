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
You are an expert technical interviewer. Evaluate the candidate’s answers against the role.
Always reply with strict JSON: {"score": <float 1-5>, "rationale": "<<=3 concise sentences>"}.
Score scale:
1 = Very poor
2 = Below average
3 = Adequate
4 = Strong
5 = Exceptional
"""

CLASSIFY_SYSTEM_PROMPT = """
You are assessing a SINGLE candidate answer for interview readiness.
Return strict JSON only: {"weak": true|false}.
weak = true if the answer shows: uncertainty, lack of knowledge, apology, excuse, deferral (e.g. "I don't know", "not sure", "can't recall", "sorry", "maybe later", "I haven't used that", etc.).
Otherwise weak = false.
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

    raw_score = payload.get("score", 1.0)

    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        score = 1.0

    # Backward compatibility: if model ignored prompt and returned 0–100, normalize.
    if score > 5.0 and score <= 100.0:
        score = score / 20.0  # 100 -> 5, 80 -> 4, etc.

    # Enforce bounds 1–5
    score = max(1.0, min(5.0, score))

    return {
        "score": score,
        "rationale": (payload.get("rationale", "") or "").strip()
    }

def classify_answer_quality(answer_text: str) -> bool:
    """
    Returns True if answer is weak/unprepared, else False.
    Uses Gemini if available; otherwise heuristic fallback.
    """
    lowered = (answer_text or "").strip().lower()
    heuristic_markers = [
        "don't know", "do not know", "not sure", "unsure", "no idea",
        "can't remember", "cannot remember", "can't recall", "cannot recall",
        "sorry", "apolog", "maybe later", "haven't used", "never used",
        "no experience", "don't have experience", "not familiar", "don't remember"
    ]
    # Heuristic early decision (fast path)
    if any(m in lowered for m in heuristic_markers):
        return True

    if not GEMINI_API_KEY:
        return False  # Without key rely only on heuristic above

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(f"{CLASSIFY_SYSTEM_PROMPT.strip()}\n\nAnswer:\n{answer_text}")
        text = getattr(resp, "text", "") or _extract_text_from_candidates(resp)
        if not text:
            return False
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            return False
        data = json.loads(match.group(0))
        return bool(data.get("weak", False))
    except Exception:
        # Fail-safe: do not classify as weak unless heuristic matched
        return False
