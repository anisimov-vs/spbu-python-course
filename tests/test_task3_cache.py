# tests/test_task3_cache.py

import pytest
from unittest.mock import Mock

from project.task3.carry import curry_explicit, cache


def test_cache_basic() -> None:
    mock_func = Mock(side_effect=lambda x: x * 2)
    cached_func = cache(capacity=5)(mock_func)
    assert cached_func(2) == 4
    assert cached_func(2) == 4
    mock_func.assert_called_once_with(2)


def test_cache_lru_eviction_is_explicit() -> None:
    mock_func = Mock(side_effect=lambda x: x)
    cached_func = cache(capacity=2)(mock_func)
    cached_func("A")
    cached_func("B")
    cached_func("A")
    cached_func("C")
    assert mock_func.call_count == 3
    mock_func.reset_mock()
    cached_func("A")
    cached_func("C")
    mock_func.assert_not_called()
    cached_func("B")
    mock_func.assert_called_once_with("B")


def test_cache_works_with_curried_function() -> None:
    mock_func = Mock(side_effect=lambda x, y: x + y)
    cached_and_curried = curry_explicit(cache(capacity=5)(mock_func), 2)
    cached_and_curried(1)(2)
    cached_and_curried(1)(2)
    mock_func.assert_called_once_with(1, 2)


def test_cache_with_default_arguments() -> None:
    call_count = 0

    @cache(capacity=2)
    def func_with_defaults(a: int, b: int = 10) -> int:
        nonlocal call_count
        call_count += 1
        return a + b

    func_with_defaults(5)
    func_with_defaults(5)
    assert call_count == 1


def test_cache_disabled_by_default_and_zero_capacity() -> None:
    mock_func1 = Mock(wraps=len)
    cached_func1 = cache()(mock_func1)
    cached_func1([1])
    cached_func1([1])
    assert mock_func1.call_count == 2
    mock_func2 = Mock(wraps=len)
    cached_func2 = cache(capacity=0)(mock_func2)
    cached_func2([1, 2])
    cached_func2([1, 2])
    assert mock_func2.call_count == 2


def test_cache_disabled_on_negative_capacity() -> None:
    mock_func = Mock(wraps=len)
    c2 = cache(capacity=-5)(mock_func)
    c2([1, 2])
    c2([1, 2])
    assert mock_func.call_count == 2


def test_cache_unhashable_bypasses() -> None:
    mock_func = Mock(side_effect=len)
    cached_func = cache(capacity=5)(mock_func)
    cached_func([1, 2, 3])
    cached_func([1, 2, 3])
    assert mock_func.call_count == 2


def test_cache_kwargs_and_order_insensitivity() -> None:
    mock_func = Mock(side_effect=lambda **kw: sum(kw.values()))
    cached = cache(capacity=2)(mock_func)
    assert cached(a=1, b=2) == 3
    assert cached(b=2, a=1) == 3
    mock_func.assert_called_once()


def test_cache_with_builtin_functions() -> None:
    abs_mock = Mock(wraps=abs)
    cached_abs = cache(capacity=5)(abs_mock)
    assert cached_abs(-10) == 10
    assert cached_abs(-10) == 10
    abs_mock.assert_called_once_with(-10)


def test_cache_with_mixed_args() -> None:
    mock_func = Mock(side_effect=lambda a, b: a + b)
    cached = cache(capacity=5)(mock_func)
    cached(1, b=2)
    cached(1, b=2)
    mock_func.assert_called_once_with(1, b=2)


def test_cache_capacity_one() -> None:
    mock_func = Mock(side_effect=lambda x: x)
    cached = cache(capacity=1)(mock_func)
    cached(1)
    cached(2)
    cached(1)
    assert mock_func.call_count == 3


def test_cache_does_not_cache_exceptions() -> None:
    mock_func = Mock(side_effect=[ValueError("Fail"), "Work"])
    cached_func = cache(capacity=5)(mock_func)
    with pytest.raises(ValueError):
        cached_func(1)
    assert cached_func(1) == "Work"
    assert mock_func.call_count == 2
