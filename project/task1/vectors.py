## @file vectors.py
## @brief Module-level vector ops (product, length, angle) without functions/classes.
## @details
## - Expects pre-injected globals: operation (str) and vectors (list/tuple of 1 or 2 lists).
## - Single upfront validation for shape and numeric finiteness; OUT computed via match/case.
## - Angle is acute: acos(|dot|/(||v1||·||v2||)) in ra dians, with clamping to [-1, 1] for stability.
## @section operations_sec Supported operations
## @par product
## @brief Scalar (dot) product of two equal-length numeric vectors.
## @details OUT = sum(x_i * y_i); inputs validated above for arity, shape, and finiteness.
## @par length
## @brief Euclidean norm of a numeric vector.
## @details OUT = sqrt(sum(x_i^2)); elements are finite numbers by unified validation.
## @par angle
## @brief Acute angle (radians) between two nonzero numeric vectors.
## @details OUT = acos(|dot|/(||v1||·||v2||)), with clamp to [-1, 1] for numerical safety.


import math
from typing import Union

__all__ = ["OUT"]

# Require pre-injected globals
_SENTINEL: object = object()
operation: str | object = globals().get("operation", _SENTINEL)  # type: ignore
vectors: list[list[Union[int, float]]] = globals().get("vectors", _SENTINEL)  # type: ignore
if operation is _SENTINEL or vectors is _SENTINEL:
    raise RuntimeError("Provide globals 'operation' and 'vectors' before import")

if not isinstance(operation, str):
    raise TypeError("'operation' must be a string")
if operation not in ("product", "length", "angle"):
    raise ValueError("Operation must be 'product', 'length' or 'angle'")

if not isinstance(vectors, (list, tuple)):
    raise ValueError("'vectors' must be a list/tuple")
if not (1 <= len(vectors) <= 2):
    raise ValueError("'vectors' must consist of exactly 1 or 2 lists/tuples")
if not all(isinstance(v, (list, tuple)) for v in vectors):
    raise TypeError("'vectors' must consist only of lists/tuples")

# Type-safe validation - iterate over each vector and validate its elements
for vec in vectors:
    if isinstance(vec, (list, tuple)):
        for x in vec:
            if not (
                isinstance(x, (int, float))
                and not isinstance(x, bool)
                and math.isfinite(float(x))
            ):
                raise TypeError(
                    "Lists in 'vectors' must contain only finite numbers (no bool/NaN/Inf)"
                )

if operation == "length" and len(vectors) != 1:
    raise ValueError("'vectors' must consist exactly 1 list for 'length' operation")
if operation in ("product", "angle") and len(vectors) != 2:
    raise ValueError(
        "'vectors' must consist exactly 2 lists for 'product'/'angle' operation"
    )

if any(len(v) == 0 for v in vectors):
    raise ValueError("Vectors must be non-empty")
if len(vectors) == 2 and len(vectors[0]) != len(vectors[1]):
    raise ValueError("The vectors must be the same length")

if len(vectors) == 1:
    v: list[Union[int, float]] = vectors[0]
else:
    v1: list[Union[int, float]] = vectors[0]
    v2: list[Union[int, float]] = vectors[1]

match operation:
    case "product":
        OUT = math.fsum(x * y for x, y in zip(v1, v2))

    case "length":
        OUT = math.sqrt(math.fsum(x * x for x in v))

    case "angle":
        dot = math.fsum(x * y for x, y in zip(v1, v2))
        l1 = math.sqrt(math.fsum(x * x for x in v1))
        l2 = math.sqrt(math.fsum(y * y for y in v2))
        if l1 == 0.0 or l2 == 0.0:
            raise ValueError("The vectors must be nonzero vectors")
        c = abs(dot) / (l1 * l2)
        c = -1.0 if c < -1.0 else (1.0 if c > 1.0 else c)
        OUT = math.acos(c)

    ## @brief invalid operation (defensive; unreachable due to early validation).
    case _:
        raise ValueError("Operation must be product, length or angle")
