import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

logger = logging.getLogger(__name__)

# Find the project root folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Find the .env file
ENV_PATH = PROJECT_ROOT / ".env"

# Load variables from .env
load_dotenv(dotenv_path=ENV_PATH)

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found.")

# Create Gemini client
client = genai.Client(api_key=api_key)


def analyze_resume(resume_text: str) -> dict:
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    prompt = f"""
You are a professional ATS resume reviewer.

Analyze this resume.

Resume:
{resume_text}

Return ONLY valid JSON in this format:

{{
  "score": 0,
  "strengths": ["", "", ""],
  "missing_skills": ["", "", ""],
  "summary": ""
}}

Rules:
- Score must be between 0 and 100.
- Return exactly 3 strengths.
- Return exactly 3 missing skills.
- Summary must be exactly one sentence.
- Do not use Markdown.
- Do not wrap the JSON inside ```json.
- Do not include any text outside the JSON.
"""

    logger.info("Resume AI analysis started")

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        logger.info("Resume AI analysis completed")

        return json.loads(response.text)

    except json.JSONDecodeError:
        logger.error("Gemini returned invalid JSON.")

        raise RuntimeError("AI returned an invalid JSON response.")

    except Exception as error:
        logger.error("Resume AI analysis failed: %s", error)

        raise RuntimeError(
            "AI resume analysis failed."
        ) from error