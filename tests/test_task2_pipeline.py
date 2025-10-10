# tests/test_task2_pipeline.py

import itertools
from functools import reduce
from typing import Callable, Iterable, Iterator, Union, cast

import pytest

from project.task2.pipeline import aggregate, pipeline, stream


@pytest.fixture()
def sample_numbers() -> list[int]:
    return [1, 2, 3, 4, 5]


@pytest.fixture()
def sample_dict() -> dict[str, int]:
    return {"a": 1, "b": 2, "c": 3}


def double(x: int) -> int:
    return x * 2


def square(x: int) -> int:
    return x**2


def is_even(x: int) -> bool:
    return x % 2 == 0


def greater_than_five(x: int) -> bool:
    return x > 5


def inc(x: int) -> int:
    return x + 1


def op_map_double(it: Iterable[object]) -> Iterable[int]:
    return map(double, cast(Iterable[int], it))


def op_filter_is_even(it: Iterable[object]) -> Iterable[int]:
    return filter(is_even, cast(Iterable[int], it))


def op_map_square(it: Iterable[object]) -> Iterable[int]:
    return map(square, cast(Iterable[int], it))


def op_filter_greater_than_five(it: Iterable[object]) -> Iterable[int]:
    return filter(greater_than_five, cast(Iterable[int], it))


def op_map_inc(it: Iterable[object]) -> Iterable[int]:
    return map(inc, cast(Iterable[int], it))


def test_stream_from_iterable(sample_numbers: list[int]) -> None:
    assert list(stream(sample_numbers)) == [1, 2, 3, 4, 5]


def test_stream_from_mapping_keys(sample_dict: dict[str, int]) -> None:
    assert set(stream(sample_dict, dict_mode="keys")) == {"a", "b", "c"}


def test_stream_from_mapping_values(sample_dict: dict[str, int]) -> None:
    assert set(stream(sample_dict, dict_mode="values")) == {1, 2, 3}


def test_stream_from_mapping_items(sample_dict: dict[str, int]) -> None:
    assert set(stream(sample_dict, dict_mode="items")) == {("a", 1), ("b", 2), ("c", 3)}


def test_stream_from_callable_count() -> None:
    it = iter([10, 20, 30, 40])

    def f() -> int:
        return next(it)

    assert list(stream(f, count=3)) == [10, 20, 30]


def test_stream_from_callable_sentinel() -> None:
    data = iter([1, 2, 3, None, 99])

    def reader() -> int | None:
        return next(data)

    assert list(stream(reader, sentinel=None)) == [1, 2, 3]


def test_pipeline_with_map() -> None:
    result = pipeline(stream(range(0, 5)), op_map_double)
    assert list(result) == [0, 2, 4, 6, 8]


def test_pipeline_with_filter() -> None:
    result = pipeline(stream(range(0, 10)), op_filter_is_even)
    assert list(result) == [0, 2, 4, 6, 8]


def test_pipeline_chained() -> None:
    result = pipeline(
        stream(range(0, 10)),
        op_map_double,
        op_filter_greater_than_five,
        op_map_inc,
    )
    assert list(result) == [7, 9, 11, 13, 15, 17, 19]


def test_pipeline_with_zip() -> None:
    def op_zip(it: Iterable[object]) -> Iterable[tuple[object, object]]:
        return zip(it, stream(range(10, 15)))

    result = pipeline(stream(range(0, 5)), op_zip)
    assert list(result) == [(0, 10), (1, 11), (2, 12), (3, 13), (4, 14)]


def test_pipeline_with_reduce_materialize_inside() -> None:
    def multiply(a: int, b: int) -> int:
        return a * b

    def op_reduce(it: Iterable[object]) -> list[int]:
        return [reduce(multiply, cast(Iterable[int], it))]

    result = pipeline(stream(range(1, 6)), op_reduce)
    assert list(result) == [120]


def test_pipeline_with_custom_generator(sample_numbers: list[int]) -> None:
    def custom_op(it: Iterable[object]) -> Iterator[int]:
        for x in cast(Iterable[int], it):
            if x % 3 == 0:
                yield x * 10

    result = pipeline(stream(sample_numbers), custom_op)
    assert list(result) == [30]


@pytest.mark.parametrize(
    "collector,expected",
    [
        (list, [0, 1, 2, 3, 4]),
        (set, {0, 1, 2, 3, 4}),
        (tuple, (0, 1, 2, 3, 4)),
    ],
)
def test_aggregate_collectors(
    collector: Callable[[Iterable[int]], Union[list[int], set[int], tuple[int, ...]]],
    expected: Union[list[int], set[int], tuple[int, ...]],
) -> None:
    assert aggregate(stream(range(0, 5)), collector) == expected


def test_aggregate_default_list() -> None:
    out = aggregate(stream(range(0, 5)))
    assert out == [0, 1, 2, 3, 4]
    assert isinstance(out, list)


def test_laziness_no_eval_until_consumed() -> None:
    seen: list[int] = []

    def track(x: int) -> int:
        seen.append(x)
        return x * 2

    def op_track(it: Iterable[object]) -> Iterable[int]:
        return map(track, cast(Iterable[int], it))

    result = pipeline(stream(range(0, 5)), op_track)
    assert len(seen) == 0
    list(result)
    assert len(seen) == 5


def test_laziness_partial_consumption() -> None:
    seen: list[int] = []

    def track(x: int) -> int:
        seen.append(x)
        return x * 2

    def op_track(it: Iterable[object]) -> Iterable[int]:
        return map(track, cast(Iterable[int], it))

    result = pipeline(stream(range(0, 1000000)), op_track)
    head = list(itertools.islice(result, 3))
    assert head == [0, 2, 4]
    assert len(seen) == 3


def test_laziness_early_termination() -> None:
    seen: list[int] = []

    def track(x: int) -> int:
        seen.append(x)
        return x * 2

    def op1(it: Iterable[object]) -> Iterable[int]:
        return map(track, cast(Iterable[int], it))

    def greater_than_ten(x: int) -> bool:
        return x > 10

    def op2(it: Iterable[object]) -> Iterable[int]:
        return filter(greater_than_ten, cast(Iterable[int], it))

    result = pipeline(stream(range(0, 100)), op1, op2)
    first = next(iter(result))
    assert first == 12
    assert len(seen) == 7


def test_laziness_infinite_callable_with_islice() -> None:
    x = -1

    def f() -> int:
        nonlocal x
        x += 1
        return x

    seq = stream(f, count=10)
    picked = list(itertools.islice(seq, 5))
    assert picked == [0, 1, 2, 3, 4]


@pytest.mark.parametrize(
    "start,stop,op,expected",
    [
        (0, 5, op_map_double, [0, 2, 4, 6, 8]),
        (0, 5, op_filter_is_even, [0, 2, 4]),
        (1, 6, op_map_square, [1, 4, 9, 16, 25]),
    ],
)
def test_pipeline_parametrized(
    start: int,
    stop: int,
    op: Callable[[Iterable[object]], Iterable[object]],
    expected: list[int],
) -> None:
    assert list(pipeline(stream(range(start, stop)), op)) == expected
