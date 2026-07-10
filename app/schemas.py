from typing import Literal, Optional
from pydantic import BaseModel, Field


class MathStepRequest(BaseModel):
    problem_type: Literal["integration", "differentiation"]
    original_expression: str
    partial_work: str
    remaining_expression: Optional[str] = None
    variable: str = "x"
    substitution: Optional[str] = None


class MathStepResponse(BaseModel):
    verified: bool
    problem_type: str
    extracted_remaining_expression: str | None
    tool_result: str | None
    final_answer: str | None
    explanation: str
    detected_text: str | None = None
    substitution: str | None = None