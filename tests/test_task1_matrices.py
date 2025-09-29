# tests/test_task1_matrices.py

import sys
import math
from pathlib import Path
from uuid import uuid4
import importlib.util
import pytest
from typing import Any, Union


ROOT = Path(__file__).resolve().parents[1]
MATRICES_PATH = ROOT / "project" / "task1" / "matrices.py"


def load_matrices_module(
    operation: str, matrices: list[list[list[Union[int, float]]]]
) -> list[list[Union[int, float]]]:
    """
    Load project/task1/matrices.py with pre-injected globals:
    - operation: str ("add" | "multiply" | "transpose")
    - matrices: list with [m1, m2] or [m]
    Returns module object with attribute out.
    """
    spec_name = f"project.task1.matrices_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(spec_name, str(MATRICES_PATH))
    assert spec and spec.loader, "Failed to create spec for matrices.py"
    mod = importlib.util.module_from_spec(spec)
    # Inject required globals before executing the module
    setattr(mod, "operation", operation)
    setattr(mod, "matrices", matrices)
    sys.modules[spec_name] = mod
    spec.loader.exec_module(mod)
    out: list[list[Union[int, float]]] = getattr(mod, "out")
    return out


def test_add_basic() -> None:
    m1: list[list[Union[int, float]]] = [[1, 2], [3, 4]]
    m2: list[list[Union[int, float]]] = [[10, 20], [30, 40]]
    out: list[list[Union[int, float]]] = load_matrices_module("add", [m1, m2])
    assert out == [[11, 22], [33, 44]]


def test_multiply_basic() -> None:
    # (2x3) · (3x2) -> (2x2)
    m1: list[list[Union[int, float]]] = [[1, 2, 3], [4, 5, 6]]
    m2: list[list[Union[int, float]]] = [[7, 8], [9, 10], [11, 12]]
    out = load_matrices_module("multiply", [m1, m2])
    assert out == [[58, 64], [139, 154]]


def test_transpose_basic() -> None:
    m0: list[list[Union[int, float]]] = [[1, 2, 3], [4, 5, 6]]
    out: list[list[Union[int, float]]] = load_matrices_module("transpose", [m0])
    assert out == [[1, 4], [2, 5], [3, 6]]


def test_missing_globals_raises_runtimeerror() -> None:
    # Import without injected globals must fail fast in the module
    spec_name = f"project.task1.matrices_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(spec_name, str(MATRICES_PATH))
    assert spec and spec.loader
    with pytest.raises(RuntimeError):
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec_name] = mod
        spec.loader.exec_module(mod)


def test_invalid_operation_raises_valueerror() -> None:
    with pytest.raises(ValueError):
        load_matrices_module("sum", [[[1]]])  # unsupported op


def test_add_wrong_arity_raises() -> None:
    with pytest.raises(ValueError):
        load_matrices_module(
            "add",
            [
                [[1, 2]],
            ],
        )  # only one matrix


def test_multiply_wrong_arity_raises() -> None:
    with pytest.raises(ValueError):
        load_matrices_module("multiply", [[[1]]])  # only one matrix


def test_transpose_wrong_arity_raises() -> None:
    with pytest.raises(ValueError):
        load_matrices_module("transpose", [[[1]], [[2]]])  # two matrices given


def test_add_dimension_mismatch_raises() -> None:
    m1: list[list[Union[int, float]]] = [[1, 2], [3, 4]]
    m2: list[list[Union[int, float]]] = [[5, 6, 7], [8, 9, 10]]
    with pytest.raises(ValueError):
        load_matrices_module("add", [m1, m2])


def test_multiply_inner_mismatch_raises() -> None:
    # (2x2) · (3x2) -> inner dims mismatch (2 != 3)
    m1: list[list[Union[int, float]]] = [[1, 2], [3, 4]]
    m2: list[list[Union[int, float]]] = [[1, 2], [3, 4], [5, 6]]
    with pytest.raises(ValueError):
        load_matrices_module("multiply", [m1, m2])


@pytest.mark.parametrize(
    "bad",
    [
        [[[float("nan")]]],  # transpose: NaN element
        [[[1.0, 2.0]], [[math.inf, 0]]],  # add: Inf
        [[[1.0, 2.0]], [[-math.inf, 0]]],
        [[[True, 2.0]], [[3.0, 4.0]]],  # bool is not allowed
    ],
)
def test_nonfinite_or_bool_elements_raise(
    bad: list[list[list[Union[int, float, bool]]]]
) -> None:
    op = "transpose" if len(bad) == 1 else "add"
    with pytest.raises((TypeError, ValueError)):
        load_matrices_module(op, bad)


def test_multiply_numerical_sanity() -> None:
    m1: list[list[Union[int, float]]] = [[1e8, 1.0], [1.0, 1e8]]
    m2: list[list[Union[int, float]]] = [[1.0, 1e8], [1e8, 1.0]]
    out: list[list[Union[int, float]]] = load_matrices_module("multiply", [m1, m2])
    # Expected:
    # [1e8*1 + 1*1e8, 1e8*1e8 + 1*1]
    # [1*1 + 1e8*1e8, 1*1e8 + 1e8*1]
    expected: list[list[float]] = [[1e8 + 1e8, 1e16 + 1.0], [1.0 + 1e16, 1e8 + 1e8]]
    assert math.isclose(out[0][0], expected[0][0], rel_tol=0.0, abs_tol=1e-3)
    assert math.isclose(out[0][1], expected[0][1], rel_tol=0.0, abs_tol=1e-3)
    assert math.isclose(out[1][0], expected[1][0], rel_tol=0.0, abs_tol=1e-3)
    assert math.isclose(out[1][1], expected[1][1], rel_tol=0.0, abs_tol=1e-3)
