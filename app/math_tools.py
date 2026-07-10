from sympy import symbols, integrate, diff, simplify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
transformations = standard_transformations + (implicit_multiplication_application,)


def clean_expression(expression: str) -> str:
    return (
        expression.replace("^", "**")
        .replace("ln", "log")
        .replace("arctan", "atan")
        .replace(" ", "")
        .strip()
    )


def solve_with_sympy(problem_type: str, expression: str, variable: str = "x") -> tuple[str, str]:
    cleaned = clean_expression(expression)

    parsed_expr = parse_expr(
        cleaned,
        transformations=transformations,
        evaluate=False,
    )

    free_symbols = list(parsed_expr.free_symbols)

    if len(free_symbols) == 1:
        actual_variable = str(free_symbols[0])
    else:
        actual_variable = variable

    var = symbols(actual_variable)

    if problem_type == "integration":
        result = integrate(parsed_expr, var)
    elif problem_type == "differentiation":
        result = diff(parsed_expr, var)
    else:
        raise ValueError("Unsupported problem type")

    return str(simplify(result)), actual_variable