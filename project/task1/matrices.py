## @file matrices.py
## @brief Matrix ops (add, multiply, transpose) at module level, no functions/classes.
## @details
## - Expects pre-injected globals: operation (str) and matrices (list with [m1, m2] or [m]).
## - Minimal shape checks only; arithmetic follows standard linear algebra definitions.
## @section operations_sec Supported operations
## @par add 
## @brief Element-wise matrix addition.
## @details Requires same shape; OUT[i][j] = m1[i][j] + m2[i][j].
## @par multiply
## @brief Matrix product A·B.
## @details Requires inner dimension match; OUT[i][j] = Σ_k m1[i][k]·m2[k][j].
## @par transpose
## @brief transpose: matrix transpose M^T.
## @details OUT[i][j] = M[j][i]; rows become columns.

import math
from typing import Union

__all__ = ["OUT"]

_SENTINEL: object = object()
operation: str | object = globals().get("operation", _SENTINEL)  # type: ignore
matrices: list[list[list[Union[int, float]]]] = globals().get("matrices", _SENTINEL)  # type: ignore
if operation is _SENTINEL or matrices is _SENTINEL:
    raise RuntimeError("Provide globals 'operation' and 'matrices' before import")

if not isinstance(operation, str):
    raise TypeError("'operation' must be a string")
if operation not in ("add", "multiply", "transpose"):
    raise ValueError("Operation must be 'add', 'multiply' or 'transpose'")

if not isinstance(matrices, list):
    raise TypeError("'matrices' must be a list")
if not (1 <= len(matrices) <= 2):
    raise ValueError(
        "'matrices' must be [m] for transpose or [m1, m2] for add/multiply"
    )

# Type-safe validation - iterate over each matrix and validate its elements
for matrix in matrices:
    if not isinstance(matrix, list):
        raise TypeError("All matrices must be lists")
    # Validate each row in the matrix
    for i in range(len(matrix)):
        row = matrix[i]
        if isinstance(row, (list, tuple)):
            for j in range(len(row)):
                x = row[j]
                if not (
                    isinstance(x, (int, float))
                    and not isinstance(x, bool)
                    and math.isfinite(float(x))
                ):
                    raise TypeError(
                        "Lists in matrices must contain only finite numbers (no bool/NaN/Inf)"
                    )

if operation == "transpose":
    if len(matrices) != 1:
        raise ValueError("For 'transpose' provide exactly one matrix: [m]")
    m = matrices[0]
else:
    if len(matrices) != 2:
        raise ValueError("For 'add'/'multiply' provide exactly two matrices: [m1, m2]")
    m1, m2 = matrices[0], matrices[1]

match operation:
    case "add":
        if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
            raise ValueError("For 'add', matrices must have identical dimensions (m×n)")
        OUT = [[m1[i][j] + m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]

    case "multiply":
        if len(m1[0]) != len(m2):
            raise ValueError("For 'multiply', inner dims must match: A(m×p)·B(p×n)")
        OUT = [
            [
                sum(m1[i][k] * m2[k][j] for k in range(len(m1[0])))
                for j in range(len(m2[0]))
            ]
            for i in range(len(m1))
        ]

    
    case "transpose":
        OUT = [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

    ## @brief invalid op (defensive).
    case _:
        raise ValueError("Operation must be 'add', 'multiply' or 'transpose'")
