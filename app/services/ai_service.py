import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from app.utils.logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

client = (
    genai.Client(api_key=API_KEY)
    if API_KEY
    else None
)


def _require_client():
    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY was not found"
        )


def _parse_json(text: str):
    cleaned = text.strip()

    # Remove ```json from the beginning
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove ``` from the end
    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    return json.loads(cleaned)


def _generate_with_retry(
    prompt: str,
    attempts: int = 3,
):
    """
    Call Gemini and automatically retry
    temporary Google/Gemini server errors.

    Attempts:
    1st request
    wait 2 seconds if failed

    2nd request
    wait 4 seconds if failed

    3rd request
    raise error if still unavailable
    """

    _require_client()

    for attempt in range(attempts):
        try:
            return client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

        except errors.ServerError as error:
            # If this was our final attempt,
            # return the error to the calling function.
            if attempt == attempts - 1:
                raise

            wait_seconds = 2 ** (attempt + 1)

            logger.warning(
                "Gemini server unavailable. "
                "Retrying in %s seconds. "
                "Attempt %s/%s",
                wait_seconds,
                attempt + 1,
                attempts,
            )

            time.sleep(wait_seconds)


def extract_requirement_keywords(
    requirement: str,
) -> list[str]:

    _require_client()

    prompt = f"""
You are extracting searchable recruitment requirements.

Return ONLY valid JSON in this exact shape:

{{"keywords": ["keyword 1", "keyword 2"]}}

Rules:
- Extract technical skills, frameworks, tools,
  platforms, role terms, and important experience phrases.
- Use short lowercase phrases.
- Include between 2 and 12 useful keywords.
- Do not include generic words such as
  candidate, person, need, looking.

Requirement:
{requirement}
"""

    try:
        response = _generate_with_retry(prompt)

        if not response.text:
            raise RuntimeError(
                "AI returned an empty response"
            )

        data = _parse_json(
            response.text
        )

        keywords = [
            str(item).strip().lower()
            for item in data.get(
                "keywords",
                [],
            )
            if str(item).strip()
        ]

        if not keywords:
            raise RuntimeError(
                "AI did not return usable "
                "requirement keywords"
            )

        return keywords[:12]

    except Exception as error:
        logger.exception(
            "AI requirement extraction failed"
        )

        raise RuntimeError(
            "AI candidate search is "
            "temporarily unavailable"
        ) from error


def prefilter_resumes(
    resumes: list[dict],
    keywords: list[str],
    limit: int = 20,
) -> list[dict]:

    scored = []

    for resume in resumes:

        text = resume[
            "resume_text"
        ].lower()

        matched = [
            keyword
            for keyword in keywords
            if keyword in text
        ]

        if not matched:
            continue

        coverage = (
            len(matched)
            / max(
                len(keywords),
                1,
            )
        )

        scored.append(
            (
                coverage,
                len(matched),
                resume,
            )
        )

    scored.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    return [
        item[2]
        for item in scored[:limit]
    ]


def rank_candidates(
    requirement: str,
    candidates: list[dict],
) -> list[dict]:

    _require_client()

    if not candidates:
        return []

    compact_candidates = [
        {
            "user_id": candidate[
                "user_id"
            ],
            "resume_id": candidate[
                "id"
            ],
            "resume_text": candidate[
                "resume_text"
            ][:8000],
        }
        for candidate in candidates
    ]

    prompt = f"""
You are a recruitment assistant comparing
candidate resumes with one hiring requirement.

Score ONLY what is supported by the resume text.
Do not invent experience.

Hiring requirement:
{requirement}

Candidates:
{json.dumps(
    compact_candidates,
    ensure_ascii=False
)}

Return ONLY a valid JSON array.

Each item must have exactly:

{{
    "user_id": 1,
    "resume_id": 1,
    "match_score": 0,
    "matched_skills": ["skill"],
    "missing_skills": ["skill"],
    "reason": "one short sentence"
}}

Rules:
- match_score must be an integer from 0 to 100.
- Rank based on the hiring requirement,
  not general resume quality.
- Missing skills are requirements not evidenced
  in the resume.
- Keep reason to one short sentence.
- Return one item for every candidate supplied.
"""

    try:
        response = _generate_with_retry(
            prompt
        )

        if not response.text:
            raise RuntimeError(
                "AI returned an empty response"
            )

        data = _parse_json(
            response.text
        )

        if not isinstance(
            data,
            list,
        ):
            raise RuntimeError(
                "AI ranking response "
                "was not a list"
            )

        return data

    except Exception as error:
        logger.exception(
            "AI candidate ranking failed"
        )

        raise RuntimeError(
            "AI candidate search is "
            "temporarily unavailable"
        ) from error


def recommendation_from_score(
    score: int,
) -> str:

    if score >= 80:
        return "Recommended"

    if score >= 60:
        return "Maybe"

    return "Not Recommended"