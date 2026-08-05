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


def analyze_resume(resume_text: str) -> str:
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    prompt = f"""
You are a professional ATS resume reviewer.

Analyze only the information present in this resume.

Resume:
{resume_text}

Return the response exactly in the following format:

Score: <score>/100

Strengths:
- <strength 1>
- <strength 2>
- <strength 3>

Missing Skills:
- <missing skill 1>
- <missing skill 2>
- <missing skill 3>

Summary:
<one sentence summary>

Rules:
- Return exactly 3 strengths.
- Return exactly 3 missing skills.
- Score must be between 0 and 100.
- Summary must contain only one sentence.
- Leave one blank line between each section.
- Do not use Markdown symbols such as **, #, or ``` .
- Do not add an introduction or extra conclusion.
- Do not invent information that is not present in the resume.
- Keep every point short and clear.
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

        return response.text.strip()

    except Exception as error:
        logger.error(
            "Resume AI analysis failed: %s",
            error,
        )

        raise RuntimeError(
            "AI resume analysis failed."
        ) from error