import base64
import json
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def extract_math_from_image(image_bytes: bytes, mime_type: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    prompt = """
You are reading a photo of a partially solved math problem.

Extract the math into JSON only.

Return exactly this JSON shape:
{
  "problem_type": "integration" or "differentiation",
  "original_expression": "Python/SymPy style original expression",
  "partial_work": "short transcription of visible student work",
  "remaining_expression": "only the expression that still needs integration or differentiation, not Integral(...)",
  "variable": "the variable of the remaining expression",
  "substitution": "substitution used by the student, or null"
}

Rules:
- Use ** for powers, not ^.
- Use atan(...) instead of arctan(...).
- Use log(...) instead of ln(...).
- If the work shows I = (1/3) integral du/u, return remaining_expression as 1/(3*u), variable as u.
- If the work uses u = atan(x**3 + 1/x**3), return substitution as u=atan(x**3 + 1/x**3).
- Do not include markdown.
- Do not include extra explanation.
"""

    interaction = client.interactions.create(
        model=model,
        input=[
            {"type": "text", "text": prompt},
            {
                "type": "image",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
                "mime_type": mime_type,
            },
        ],
    )

    raw_text = interaction.output_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Gemini did not return valid JSON: {raw_text}") from exc