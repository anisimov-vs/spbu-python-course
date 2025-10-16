# tests/test_task3_carry.py

import pytest
from unittest.mock import Mock
from typing import Any

from project.task3.carry import curry_explicit, uncurry_explicit


def test_curry_basic_functionality() -> None:
    f = lambda x, y, z: x + y + z
    curried_f = curry_explicit(f, 3)
    assert curried_f(1)(2)(3) == 6


def test_curry_accepts_only_one_argument_per_call() -> None:
    f = lambda x, y: x + y
    curried_f = curry_explicit(f, 2)
    with pytest.raises(TypeError):
        curried_f(1, 2)


def test_curry_arity_one_explicit() -> None:
    def f(x: int) -> int:
        return x * 2

    curried = curry_explicit(f, 1)
    assert curried(5) == f(5)


def test_curry_arity_zero_double_parens() -> None:
    def get_value() -> int:
        return 42

    curried = curry_explicit(get_value, 0)
    assert curried() == get_value()
    assert callable(curried)


def test_curry_task_example_exact() -> None:
    f2 = curry_explicit((lambda x, y, z: f"<{x},{y},{z}>"), 3)
    assert f2(123)(456)(562) == "<123,456,562>"


def test_curry_arity_overflow_fails() -> None:
    f = lambda x: x
    curried_f = curry_explicit(f, 1)
    with pytest.raises(TypeError):
        curried_f(1)(2)


def test_curry_with_builtin_arbitrary_arity_function() -> None:
    mock_print = Mock()
    mock_print.return_value = None
    curried_print = curry_explicit(mock_print, 2)
    result = curried_print(1)(2)
    mock_print.assert_called_once_with(1, 2)
    assert result is None


def test_curry_explicit_negative_arity() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        curry_explicit(lambda x: x, -1)


def test_curry_non_integer_arity() -> None:
    with pytest.raises(ValueError):
        bad_arity: Any = "2"
        curry_explicit(lambda: None, bad_arity)


def test_curry_arity_larger_than_params_succeeds_until_call() -> None:
    f = lambda x: x
    curried = curry_explicit(f, 2)
    with pytest.raises(TypeError):
        curried(1)(2)


def test_curry_zero_arity_with_arg_fails() -> None:
    curried = curry_explicit(lambda: 42, 0)
    with pytest.raises(TypeError):
        curried(1)


def test_uncurry_basic_functionality() -> None:
    f = lambda x, y, z: x * y * z
    curried_f = curry_explicit(f, 3)
    uncurried_f = uncurry_explicit(curried_f, 3)
    assert uncurried_f(2, 3, 4) == 24


def test_uncurry_arity_zero() -> None:
    mock_func = Mock(return_value="called")
    curried_f = curry_explicit(mock_func, 0)
    uncurried_f = uncurry_explicit(curried_f, 0)
    result = uncurried_f()
    assert result == "called"
    mock_func.assert_called_once()


def test_uncurry_negative_arity() -> None:
    with pytest.raises(ValueError):
        uncurry_explicit(lambda x: x, -1)


def test_uncurry_too_many_args() -> None:
    f = lambda a, b: a + b
    cur = curry_explicit(f, 2)
    uncur = uncurry_explicit(cur, 2)
    with pytest.raises(TypeError):
        uncur(1, 2, 3)


def test_uncurry_too_few_args() -> None:
    f = lambda x, y, z: x + y + z
    curried = curry_explicit(f, 3)
    uncurried = uncurry_explicit(curried, 3)
    with pytest.raises(TypeError):
        uncurried(1, 2)


def test_curry_returns_callable_when_partially_applied() -> None:
    f = lambda x, y, z: f"<{x},{y},{z}>"
    curried = curry_explicit(f, 3)
    partial1 = curried(1)
    assert callable(partial1)
    partial2 = partial1(2)
    assert callable(partial2)
    result = partial2(3)
    assert result == "<1,2,3>"


# Cache Tests
