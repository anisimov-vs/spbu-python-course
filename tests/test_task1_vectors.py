# tests/test_task1_vectors.py

import sys
import math
from pathlib import Path
from uuid import uuid4
import importlib.util
import pytest
from typing import Union


ROOT = Path(__file__).resolve().parents[1]
VECTORS_PATH = ROOT / "project" / "task1" / "vectors.py"


def load_vectors_module(
    operation: str, vectors: list[list[Union[int, float]]]
) -> float:
    """
    Load project/task1/vectors.py with pre-injected globals:
    - operation: str
    - vectors: list of one or two lists (numeric)
    Returns the loaded module object with attribute out.
    """
    spec_name = f"project.task1.vectors_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(spec_name, str(VECTORS_PATH))
    assert spec and spec.loader, "Failed to create spec for vectors.py"
    mod = importlib.util.module_from_spec(spec)
    # Inject required globals before executing the module
    setattr(mod, "operation", operation)
    setattr(mod, "vectors", vectors)
    sys.modules[spec_name] = mod
    spec.loader.exec_module(mod)
    out: float = getattr(mod, "out")
    return out


def test_product_basic() -> None:
    out: float = load_vectors_module("product", [[1, 2, 3], [4, 5, 6]])
    assert out == 32.0


def test_length_basic() -> None:
    out: float = load_vectors_module("length", [[3, 4]])
    assert math.isclose(out, 5.0, rel_tol=0.0, abs_tol=1e-12)


def test_angle_perpendicular() -> None:
    out: float = load_vectors_module("angle", [[1.0, 0.0], [0.0, 1.0]])
    assert math.isclose(out, math.pi / 2.0, rel_tol=0.0, abs_tol=1e-15)


def test_angle_opposite_vectors_is_zero() -> None:
    # abs(dot) -> acute angle; for opposite vectors angle = 0
    out: float = load_vectors_module("angle", [[1.0, 0.0], [-1.0, 0.0]])
    assert math.isclose(out, 0.0, rel_tol=0.0, abs_tol=1e-15)


def test_missing_globals_raises_runtimeerror() -> None:
    # Import without injected globals must fail fast in the module
    spec_name = f"project.task1.vectors_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(spec_name, str(VECTORS_PATH))
    assert spec and spec.loader
    with pytest.raises(RuntimeError):
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec_name] = mod
        spec.loader.exec_module(mod)


def test_invalid_operation_raises_valueerror() -> None:
    with pytest.raises(ValueError):
        load_vectors_module("sum", [[1, 2, 3], [4, 5, 6]])


def test_wrong_arity_for_length_raises() -> None:
    with pytest.raises(ValueError):
        load_vectors_module("length", [[1, 2], [3, 4]])


def test_wrong_arity_for_product_raises() -> None:
    with pytest.raises(ValueError):
        load_vectors_module("product", [[1, 2, 3]])


def test_wrong_arity_for_angle_raises() -> None:
    with pytest.raises(ValueError):
        load_vectors_module("angle", [[1, 2, 3]])


def test_mismatched_lengths_raises() -> None:
    with pytest.raises(ValueError):
        load_vectors_module("product", [[1, 2], [3]])


def test_empty_vector_raises() -> None:
    with pytest.raises(ValueError):
        load_vectors_module("product", [[], []])


@pytest.mark.parametrize(
    "bad_vectors",
    [
        [[float("nan"), 1.0], [2.0, 3.0]],
        [[float("inf"), 1.0], [2.0, 3.0]],
        [[1.0, 2.0], [3.0, float("-inf")]],
        [[True, 1.0], [2.0, 3.0]],
    ],
)
def test_nonfinite_or_bool_elements_raise_typeerror(
    bad_vectors: list[list[Union[int, float, bool]]]
) -> None:
    with pytest.raises(TypeError):
        load_vectors_module("product", bad_vectors)


def test_product_is_sum_of_pairwise_products() -> None:
    v1 = [1e16, 1.0, -1e16]
    v2 = [1.0, 1e16, -1.0]

    out: float = load_vectors_module("product", [v1, v2])
    assert math.isclose(out, 3e16, rel_tol=0.0, abs_tol=1e7)
