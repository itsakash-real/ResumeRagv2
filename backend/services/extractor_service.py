

import json
import logging
import os
import time

from dotenv import load_dotenv
from fastapi import HTTPException, status
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in environment variables.")

# Module-level client — instantiated once, reused for all requests
client = Groq(api_key=GROQ_API_KEY)

REQUIRED_KEYS = {"skills", "experience_years", "job_titles", "summary"}

SYSTEM_PROMPT = (
    "You are a resume parser. "
    "Return ONLY valid JSON. No markdown, no explanation, no preamble."
)

USER_PROMPT_TEMPLATE = (
    "Extract structured data from this resume:\n\n"
    "{raw_text}\n\n"
    "Return JSON with exactly these keys:\n"
    "- skills: list of strings (max 15)\n"
    "- experience_years: integer\n"
    "- job_titles: list of strings\n"
    "- summary: string (2 sentences max)"
)


def extract_profile(raw_text: str) -> dict:
    """
    Sends resume text to Groq (Llama 3.3 70B) and returns a structured profile.

    The model is instructed to return strict JSON. Any markdown fencing
    (```json ... ```) is stripped before parsing.

    Args:
        raw_text: Plain-text content of the resume.

    Returns:
        Dict with keys: skills, experience_years, job_titles, summary.

    Raises:
        HTTPException 502: If Groq API call fails or returns malformed JSON.
        HTTPException 422: If the response JSON is missing required keys.
    """
    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": USER_PROMPT_TEMPLATE.format(raw_text=raw_text),
                },
            ],
            temperature=0.1,
            max_tokens=1000,
        )
    except Exception as exc:
        logger.exception("Groq API call failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Profile extraction service is temporarily unavailable.",
        ) from exc

    elapsed = time.perf_counter() - start
    logger.info("Groq extraction completed in %.3fs", elapsed)

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model includes them despite instructions
    clean = raw.replace("```json", "").replace("```", "").strip()

    try:
        parsed: dict = json.loads(clean)
    except json.JSONDecodeError as exc:
        logger.error("Groq returned non-JSON content: %r", clean[:200])
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Profile extraction returned an invalid response. Please retry.",
        ) from exc

    missing = REQUIRED_KEYS - parsed.keys()
    if missing:
        logger.error("Groq response missing required keys: %s", missing)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Profile extraction response is incomplete. Missing: {missing}",
        )

    # Coerce types defensively — LLMs sometimes return strings for integers
    try:
        parsed["experience_years"] = int(parsed["experience_years"])
        parsed["skills"] = [str(s) for s in parsed["skills"][:15]]
        parsed["job_titles"] = [str(t) for t in parsed["job_titles"]]
        parsed["summary"] = str(parsed["summary"])
    except (TypeError, ValueError) as exc:
        logger.error("Type coercion failed on Groq response: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Profile extraction returned unexpected data types.",
        ) from exc

    return parsed