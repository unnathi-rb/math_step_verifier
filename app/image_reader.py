

import base64
import json
import os
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()


def clean_json_response(text: str) -> str:
    cleaned = text.strip()

    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return match.group(0)

    return cleaned


def extract_math_from_image(image_bytes: bytes, mime_type: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    prompt = """
You are reading a photo of a partially solved math problem.

Extract the math into valid JSON only.

Return exactly this JSON shape:
{
  "problem_type": "integration",
  "original_expression": "Python/SymPy style original expression",
  "partial_work": "short transcription of visible student work",
  "remaining_expression": "only the expression that still needs solving, not Integral(...)",
  "variable": "x",
  "substitution": null
}

Rules:
- Return raw JSON only.
- Do not wrap the JSON in markdown.
- Do not use ```json.
- Use ** for powers, not ^.
- Use exp(x), sin(x), cos(x), tan(x), log(x), atan(x).
- remaining_expression must be a plain SymPy expression, not an equation and not Integral(...).
- If the image shows the last unresolved integral, extract only its integrand.
- If unsure, choose the simplest remaining expression visible.
"""

    response = client.models.generate_content(
        model=model,
        contents=[
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(image_bytes).decode("utf-8"),
                }
            },
            prompt,
        ],
    )

    raw_text = response.text.strip()
    cleaned_text = clean_json_response(raw_text)

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Gemini did not return valid JSON after cleanup: {cleaned_text}") from exc