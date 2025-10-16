# tests/test_task3_smart_args.py

import pytest
import random
from typing import Any, Union, cast

from project.task3.carry import curry_explicit, cache

from project.task3.smart_args import Isolated, Evaluated, smart_args


def test_smart_args_isolated_deep_copy() -> None:
    @smart_args
    def modify_dict(
        *, d: Union[dict[str, str], Isolated] = Isolated()
    ) -> dict[str, str]:
        return cast(dict[str, str], d)

    original = {"value": "original"}
    result = modify_dict(d=original)
    result["value"] = "modified"
    assert result["value"] == "modified"
    assert original["value"] == "original"


def test_smart_args_isolated_deep_copy_nested() -> None:
    @smart_args
    def g(
        *, d: Union[dict[str, dict[str, int]], Isolated] = Isolated()
    ) -> dict[str, dict[str, int]]:
        result = cast(dict[str, dict[str, int]], d)
        result["k"]["z"] = 5
        return result

    src = {"k": {"z": 0}}
    out = g(d=src)
    assert out["k"]["z"] == 5 and src["k"]["z"] == 0


def test_smart_args_isolated_requires_argument() -> None:
    @smart_args
    def f(*, x: Union[Any, Isolated] = Isolated()) -> Any:
        return x

    with pytest.raises(TypeError, match="Missing required argument"):
        f()


def test_smart_args_positional_isolated_is_still_required() -> None:
    @smart_args(positional_support=True)
    def f(x: Union[Any, Isolated] = Isolated()) -> Any:
        return x

    with pytest.raises(TypeError, match="Missing required argument"):
        f()


def test_smart_args_evaluated_dynamic_default() -> None:
    counter = 0

    def get_next() -> int:
        nonlocal counter
        counter += 1
        return counter

    @smart_args
    def func(*, dynamic_val: Union[int, Evaluated] = Evaluated(get_next)) -> int:
        return cast(int, dynamic_val)

    assert func() == 1
    assert func() == 2


def test_smart_args_does_not_execute_passed_evaluated_object() -> None:
    @smart_args
    def func(*, arg: Union[Any, Evaluated] = Evaluated(lambda: "default")) -> Any:
        return arg

    passed_in_eval = Evaluated(lambda: "passed")
    result = func(arg=passed_in_eval)
    assert result is passed_in_eval


def test_smart_args_exact_task_example_with_random() -> None:
    def get_random_number() -> int:
        return random.randint(0, 100_000)

    @smart_args
    def check_evaluation(
        *,
        x: int = get_random_number(),
        y: Union[int, Evaluated] = Evaluated(get_random_number),
    ) -> tuple[int, int]:
        return x, cast(int, y)

    x1, y1 = check_evaluation()
    x2, y2 = check_evaluation()
    x3, y3 = check_evaluation(y=150)
    assert x1 == x2 == x3
    assert y1 != y2
    assert y3 == 150


def test_smart_args_with_mixed_defaults() -> None:
    @smart_args
    def func(
        a: int, b: int = 10, *, c: Union[str, Evaluated] = Evaluated(lambda: "dynamic")
    ) -> tuple[int, int, str]:
        return a, b, cast(str, c)

    a, b, c = func(5)
    assert a == 5 and b == 10 and c == "dynamic"


def test_smart_args_with_mixed_params_and_star_args() -> None:
    counter = 0

    def inc() -> int:
        nonlocal counter
        counter += 1
        return counter

    @smart_args(positional_support=True)
    def f(
        a: Union[list[int], Isolated] = Isolated(),
        *args: Any,
        b: Union[int, Evaluated] = Evaluated(inc),
        **kwargs: Any,
    ) -> tuple[list[int], tuple[Any, ...], int, dict[str, Any]]:
        return cast(list[int], a), args, cast(int, b), kwargs

    my_list = [1, 2]
    a_res, args_res, b_res, kwargs_res = f(my_list, 10, 20, c=30, d=40)
    assert a_res == [1, 2] and my_list is not a_res
    assert args_res == (10, 20) and b_res == 1 and kwargs_res == {"c": 30, "d": 40}
    _, _, b_res_2, _ = f(my_list)
    assert b_res_2 == 2


def test_smart_args_positional_support_enabled() -> None:
    @smart_args(positional_support=True)
    def func(pos_val: Union[str, Evaluated] = Evaluated(lambda: "dynamic")) -> str:
        return cast(str, pos_val)

    assert func() == "dynamic"
    assert func("static") == "static"


def test_smart_args_positional_fails_without_support() -> None:
    with pytest.raises(AssertionError):

        @smart_args
        def f(x: Union[Any, Isolated] = Isolated()) -> None:
            pass


def test_smart_args_positional_isolated() -> None:
    @smart_args(positional_support=True)
    def f(x: Union[list[int], Isolated] = Isolated()) -> list[int]:
        result = cast(list[int], x)
        result.append(999)
        return result

    lst = [1, 2]
    result = f(lst)
    assert result == [1, 2, 999] and lst == [1, 2]


def test_smart_args_positional_nested_isolation() -> None:
    @smart_args(positional_support=True)
    def f(
        data: Union[dict[str, dict[str, int]], Isolated] = Isolated()
    ) -> dict[str, dict[str, int]]:
        result = cast(dict[str, dict[str, int]], data)
        result["nested"]["value"] = 999
        return result

    original = {"nested": {"value": 1}}
    result = f(original)
    assert result["nested"]["value"] == 999 and original["nested"]["value"] == 1


def test_smart_args_positional_evaluated() -> None:
    counter = 0

    def inc() -> int:
        nonlocal counter
        counter += 1
        return counter

    @smart_args(positional_support=True)
    def f(x: Union[int, Evaluated] = Evaluated(inc)) -> int:
        return cast(int, x)

    assert f() == 1 and f() == 2


def test_smart_args_no_combination_error() -> None:
    class Combined(Isolated, Evaluated):
        def __init__(self) -> None:
            Evaluated.__init__(self, lambda: "dummy")

    with pytest.raises(AssertionError, match="Cannot combine Isolated and Evaluated"):

        @smart_args
        def func(*, arg: Union[Any, Combined] = Combined()) -> None:
            pass


def test_smart_args_evaluating_isolated_class_fails() -> None:
    with pytest.raises(AssertionError, match="Cannot combine Isolated and Evaluated"):

        @smart_args
        def f(*, arg: Union[Any, Evaluated] = Evaluated(Isolated)) -> None:
            pass


def test_smart_args_evaluating_isolated_instance_fails() -> None:
    @smart_args
    def f(*, arg: Union[Any, Evaluated] = Evaluated(lambda: Isolated())) -> Any:
        return arg

    with pytest.raises(AssertionError):
        f()


def test_smart_args_on_class_method() -> None:
    class MyClass:
        @smart_args
        def my_method(
            self, *, data: Union[dict[str, Any], Isolated] = Isolated()
        ) -> dict[str, Any]:
            result = cast(dict[str, Any], data)
            result["self"] = self
            return result

    instance = MyClass()
    original_data: dict[str, Any] = {}
    result = instance.my_method(data=original_data)
    assert result["self"] is instance and original_data == {}


def test_smart_args_isolated_with_immutable() -> None:
    @smart_args
    def func(*, num: Union[int, Isolated] = Isolated()) -> int:
        return cast(int, num) + 1

    assert func(num=5) == 6


def test_evaluated_requires_callable() -> None:
    with pytest.raises(TypeError):
        val: Any = 123
        Evaluated(val)


def test_metadata_preservation() -> None:
    @cache(capacity=5)
    @smart_args
    def my_func(*, a: Union[Any, Isolated] = Isolated()) -> Any:
        """This is a docstring."""
        return a

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "This is a docstring."


def test_all_decorators_stacked() -> None:
    call_count = 0

    def real_func(a: tuple[int, ...], b: tuple[int, ...]) -> int:
        nonlocal call_count
        call_count += 1
        return a[0] + b[0]

    @cache(capacity=5)
    @smart_args(positional_support=True)
    def base_func(
        a: Union[tuple[int, ...], Isolated] = Isolated(),
        b: Union[tuple[int, ...], Isolated] = Isolated(),
    ) -> int:
        return real_func(cast(tuple[int, ...], a), cast(tuple[int, ...], b))

    decorated_func = curry_explicit(base_func, 2)
    arg1 = (10,)
    arg2 = (20,)
    decorated_func(arg1)(arg2)
    decorated_func(arg1)(arg2)
    assert call_count == 1
