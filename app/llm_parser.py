import re


def extract_remaining_expression(partial_work: str, given_remaining: str | None = None) -> str:
    """
    V1 parser.

    For the resume project, we keep input slightly structured.
    Best format:
    remaining expression: 2*x*cos(x)

    Later, you can replace this file with a real LLM call.
    """

    if given_remaining:
        return given_remaining.strip()

    patterns = [
        r"remaining expression\s*:\s*(.+)",
        r"leftover expression\s*:\s*(.+)",
        r"stuck at\s*:\s*(.+)",
        r"remaining integral\s*:\s*(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, partial_work, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    raise ValueError(
        "Could not extract remaining expression. Please include: remaining expression: ..."
    )