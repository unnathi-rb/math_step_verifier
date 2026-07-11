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
    )


def format_final_answer(expression: str | None) -> str | None:
    if expression is None:
        return None

    if expression == "ln(u)/3":
        return "1/3 ln(u)"

    if expression.startswith("ln((") and expression.endswith("))/3"):
        inner = expression[4:-4]
        return f"1/3 ln({inner})"

    if expression.startswith("ln(") and expression.endswith(")/3"):
        inner = expression[3:-3]
        return f"1/3 ln({inner})"

    return expression


def build_integration_steps(
    remaining_expression: str,
    tool_result: str,
    variable: str,
    substitution: str | None = None,
) -> list[str]:
    compact_expression = remaining_expression.replace(" ", "")
    pretty_expression = pretty_math(remaining_expression)
    pretty_result = format_final_answer(pretty_math(tool_result))
    pretty_substitution = pretty_math(substitution)

    steps = [
        f"Continue from the unresolved integral: ∫ {pretty_expression} d{variable}.",
    ]

    if "/" in compact_expression and variable in compact_expression:
        if f"1/{variable}" in compact_expression or f"/{variable}" in compact_expression:
            steps.append(
                f"Recognize the logarithmic form: ∫ 1/{variable} d{variable} = ln({variable})."
            )
            steps.append("Apply the constant multiple rule if there is a coefficient outside the variable.")
        else:
            steps.append("Recognize this as a rational expression.")
            steps.append("Use symbolic integration to simplify and integrate the rational expression.")

    elif "exp" in compact_expression:
        steps.append("Recognize the exponential function in the expression.")

        if variable in compact_expression:
            steps.append(
                "If the expression also has a polynomial factor, use integration by parts or symbolic integration."
            )
        else:
            steps.append("Integrate the exponential term using the standard exponential rule.")

    elif "sin" in compact_expression or "cos" in compact_expression or "tan" in compact_expression:
        steps.append("Recognize the trigonometric expression.")
        steps.append("Apply the matching trigonometric integration rule or identity.")

    elif f"{variable}**" in compact_expression or f"{variable}^" in compact_expression:
        steps.append("Recognize the polynomial-style expression.")
        steps.append("Apply the power rule for integration term by term.")

    else:
        steps.append("Use symbolic integration to continue from this expression.")

    steps.append(f"The computed continuation is: {pretty_result}.")

    if substitution and "=" in substitution:
        left_side, replacement = pretty_substitution.split("=", 1)
        steps.append(f"The earlier substitution was {left_side.strip()} = {replacement.strip()}.")
        steps.append("Substitute back to express the result using the original variable.")

    steps.append("Add the constant of integration: C.")
    return steps


def build_steps(
    problem_type: str,
    remaining_expression: str,
    tool_result: str,
    variable: str,
    substitution: str | None = None,
) -> list[str]:
    pretty_expression = pretty_math(remaining_expression)
    pretty_result = pretty_math(tool_result)

    if problem_type == "integration":
        return build_integration_steps(
            remaining_expression=remaining_expression,
            tool_result=tool_result,
            variable=variable,
            substitution=substitution,
        )

    if problem_type == "differentiation":
        return [
            f"Continue from the expression to differentiate: {pretty_expression}.",
            f"Differentiate the expression with respect to {variable}.",
            f"The computed derivative is: {pretty_result}.",
            "No constant of integration is needed for differentiation.",
        ]

    return ["Unsupported problem type."]


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
        pretty_tool_result = format_final_answer(pretty_math(tool_result))
        pretty_substitution = pretty_math(request.substitution)

        if request.problem_type == "integration":
            final_answer = f"The remaining part integrates to: {pretty_tool_result} + C"

            if request.substitution and "=" in request.substitution:
                left_side, replacement = request.substitution.split("=", 1)
                left_side = left_side.strip()
                replacement = replacement.strip()

                substituted_result = tool_result.replace(left_side, f"({replacement})")
                pretty_substituted_result = format_final_answer(
                    pretty_math(substituted_result)
                )

                final_answer = (
                    f"The remaining part integrates to: {pretty_tool_result}. "
                    f"Using {pretty_substitution}, final answer is: "
                    f"{pretty_substituted_result} + C"
                )

        else:
            final_answer = f"The derivative is: {pretty_tool_result}"

        steps = build_steps(
            problem_type=request.problem_type,
            remaining_expression=remaining_expression,
            tool_result=tool_result,
            variable=actual_variable,
            substitution=request.substitution,
        )

        return MathStepResponse(
            verified=True,
            problem_type=request.problem_type,
            extracted_remaining_expression=pretty_remaining_expression,
            tool_result=pretty_tool_result,
            final_answer=final_answer,
            explanation=f"The expression was solved with respect to {actual_variable} using SymPy.",
            substitution=pretty_substitution,
            steps=steps,
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
            steps=[],
        )