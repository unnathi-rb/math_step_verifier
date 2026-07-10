from app.schemas import MathStepRequest, MathStepResponse
from app.llm_parser import extract_remaining_expression
from app.math_tools import solve_with_sympy


def pretty_math(expression: str | None) -> str | None:
    if expression is None:
        return None

    return (
        expression
        .replace("log", "ln")
        .replace("atan", "arctan")
        .replace("**", "^")
        .replace("*", "")
    )


def verify_math_step(request: MathStepRequest) -> MathStepResponse:
    try:
        remaining_expression = extract_remaining_expression(
            partial_work=request.partial_work,
            given_remaining=request.remaining_expression,
        )

        tool_result, actual_variable = solve_with_sympy(
            problem_type=request.problem_type,
            expression=remaining_expression,
            variable=request.variable,
        )

        pretty_remaining_expression = pretty_math(remaining_expression)
        pretty_tool_result = pretty_math(tool_result)
        pretty_substitution = pretty_math(request.substitution)

        if request.problem_type == "integration":
            final_answer = f"The remaining part integrates to: {pretty_tool_result} + C"

            if request.substitution and "=" in request.substitution:
                left_side, replacement = request.substitution.split("=", 1)
                left_side = left_side.strip()
                replacement = replacement.strip()

                substituted_result = tool_result.replace(left_side, f"({replacement})")
                pretty_substituted_result = pretty_math(substituted_result)

                final_answer = (
                    f"The remaining part integrates to: {pretty_tool_result}. "
                    f"Using {pretty_substitution}, final answer is: "
                    f"{pretty_substituted_result} + C"
                )

        else:
            final_answer = f"The derivative is: {pretty_tool_result}"

        return MathStepResponse(
            verified=True,
            problem_type=request.problem_type,
            extracted_remaining_expression=pretty_remaining_expression,
            tool_result=pretty_tool_result,
            final_answer=final_answer,
            explanation=f"The expression was solved with respect to {actual_variable} using SymPy.",
            substitution=pretty_substitution,
        )

    except Exception as exc:
        return MathStepResponse(
            verified=False,
            problem_type=request.problem_type,
            extracted_remaining_expression=None,
            tool_result=None,
            final_answer=None,
            explanation=str(exc),
            substitution=pretty_math(request.substitution),
        )