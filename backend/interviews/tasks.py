import asyncio
import threading
import logging
from textwrap import dedent

from asgiref.sync import sync_to_async

from interviews.models import Interview, SMSMessages, InterviewQuestion
from interviews.gemini import score_interview_responses

logger = logging.getLogger(__name__)

def queue_interview_analysis(interview_id):
    threading.Thread(
        target=lambda: asyncio.run(_analyze_interview(interview_id)),
        daemon=True,
        name=f"interview-analysis-{interview_id}"
    ).start()

@sync_to_async
def _fetch_interview(interview_id):
    try:
        return Interview.objects.select_related("candidate", "job").get(pk=interview_id)
    except Interview.DoesNotExist:
        return None

@sync_to_async
def _fetch_messages(interview_id):
    return list(
        SMSMessages.objects.filter(interview_id=interview_id)
        .order_by("created_at")
        .values("direction", "message_text", "related_question_id", "created_at")
    )

@sync_to_async
def _fetch_questions(interview_id):
    return list(
        InterviewQuestion.objects.filter(interview_id=interview_id)
        .order_by("sequence_number")
        .values("id", "sequence_number", "question_text", "question_type")
    )

@sync_to_async
def _persist_score(interview_id, score):
    Interview.objects.filter(pk=interview_id).update(job_fit_score=score)

async def _analyze_interview(interview_id):
    interview = await _fetch_interview(interview_id)
    if not interview:
        logger.warning("Interview %s not found for scoring.", interview_id)
        return

    messages = await _fetch_messages(interview_id)
    if not messages:
        logger.info("No SMS transcript found for interview %s; skipping scoring.", interview_id)
        return

    questions = await _fetch_questions(interview_id)
    prompt = _build_prompt(interview, messages, questions)

    try:
        result = await score_interview_responses(prompt)
    except Exception as exc:
        logger.exception("Gemini scoring failed for interview %s: %s", interview_id, exc)
        return

    score = result.get("score")
    if score is None:
        logger.warning("Gemini response missing score for interview %s.", interview_id)
        return

    await _persist_score(interview_id, score)
    logger.info("Interview %s scored at %.2f/100.", interview_id, score)

def _build_prompt(interview, messages, questions):
    candidate = interview.candidate
    job = interview.job
    question_lines = "\n".join(
        f"- ({q.get('sequence_number') or idx + 1}) [{q.get('question_type', 'n/a')}] {q['question_text']}"
        for idx, q in enumerate(questions)
    ) or "- No structured questions recorded."

    transcript_lines = "\n".join(
        f"{'Interviewer' if msg['direction'] == 'outbound' else 'Candidate'} "
        f"[{msg['created_at']}]: {msg['message_text']}"
        for msg in messages
    )

    return dedent(f"""
    Candidate: {candidate.first_name} {candidate.last_name} ({candidate.email})
    Role Applied: {job.title if job else 'N/A'}
    Job Category: {job.category if job else 'N/A'}
    Job Description (excerpt): {(job.description[:800] + '...') if job and job.description else 'N/A'}

    Interview Questions:
    {question_lines}

    SMS Transcript:
    {transcript_lines}
    """).strip()
