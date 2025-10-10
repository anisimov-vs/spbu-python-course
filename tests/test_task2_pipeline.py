# tests/test_task2_pipeline.py

import itertools
from functools import partial, reduce
import pytest

from project.task2.pipeline import stream, pipeline, aggregate


# Fixtures
@pytest.fixture
def sample_numbers() -> list[int]:
    return [1, 2, 3, 4, 5]


@pytest.fixture
def sample_dict() -> dict[str, int]:
    return {"a": 1, "b": 2, "c": 3}


# Helper functions

def double(x: int) -> int:
    return x * 2


def square(x: int) -> int:
    return x ** 2


def is_even(x: int) -> bool:
    return x % 2 == 0


def greater_than_five(x: int) -> bool:
    return x > 5


def inc(x: int) -> int:
    return x + 1


# stream() source unification

def test_stream_from_iterable(sample_numbers):
    assert list(stream(sample_numbers)) == [1, 2, 3, 4, 5]


def test_stream_from_mapping_keys(sample_dict):
    assert set(stream(sample_dict, dict_mode="keys")) == {"a", "b", "c"}


def test_stream_from_mapping_values(sample_dict):
    assert set(stream(sample_dict, dict_mode="values")) == {1, 2, 3}


def test_stream_from_mapping_items(sample_dict):
    assert set(stream(sample_dict, dict_mode="items")) == {("a", 1), ("b", 2), ("c", 3)}


def test_stream_from_slice():
    assert list(stream(slice(0, 6, 2))) == [0, 2, 4]


def test_stream_from_numeric_tuple():
    assert list(stream((5,))) == [0, 1, 2, 3, 4]
    assert list(stream((1, 5))) == [1, 2, 3, 4]
    assert list(stream((1, 6, 2))) == [1, 3, 5]


def test_stream_from_callable_count():
    it = iter([10, 20, 30, 40])
    def f():
        return next(it)
    assert list(stream(f, count=3)) == [10, 20, 30]


def test_stream_from_callable_sentinel():
    data = iter([1, 2, 3, None, 99])
    def reader():
        return next(data)
    
    assert list(stream(reader, sentinel=None)) == [1, 2, 3]


# pipeline composition with built-ins

def test_pipeline_with_map():
    result = pipeline(stream((0, 5)), partial(map, double))
    assert list(result) == [0, 2, 4, 6, 8]


def test_pipeline_with_filter():
    result = pipeline(stream((0, 10)), partial(filter, is_even))
    assert list(result) == [0, 2, 4, 6, 8]


def test_pipeline_chained():
    result = pipeline(
        stream((0, 10)),
        partial(map, double),
        partial(filter, greater_than_five),
        partial(map, inc),
    )
    assert list(result) == [7, 9, 11, 13, 15, 17, 19]


def test_pipeline_with_zip():
    result = pipeline(
        stream((0, 5)),
        lambda it: zip(it, stream(slice(10, 15))),
    )
    assert list(result) == [(0, 10), (1, 11), (2, 12), (3, 13), (4, 14)]


def test_pipeline_with_reduce_materialize_inside():
    result = pipeline(
        stream((1, 6)),
        lambda it: [reduce(lambda a, b: a * b, it)],
    )
    assert list(result) == [120]


# Custom user operation

def test_pipeline_with_custom_generator(sample_numbers):
    def custom_op(it):
        for x in it:
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
def test_aggregate_collectors(collector, expected):
    assert aggregate(stream((0, 5)), collector) == expected


def test_aggregate_default_list():
    out = aggregate(stream((0, 5)))
    assert out == [0, 1, 2, 3, 4]
    assert isinstance(out, list)


# Laziness demonstrations

def test_laziness_no_eval_until_consumed():
    seen = []
    def track(x):
        seen.append(x)
        return x * 2
    result = pipeline(stream((0, 5)), partial(map, track))
    assert len(seen) == 0  # not evaluated yet
    list(result)
    assert len(seen) == 5


def test_laziness_partial_consumption():
    seen = []
    def track(x):
        seen.append(x)
        return x * 2
    result = pipeline(stream((0, 1000000)), partial(map, track))
    head = list(itertools.islice(result, 3))
    assert head == [0, 2, 4]
    assert len(seen) == 3


def test_laziness_early_termination():
    seen = []
    def track(x):
        seen.append(x)
        return x * 2
    result = pipeline(stream((0, 100)), partial(map, track), partial(filter, lambda x: x > 10))
    first = next(iter(result))
    assert first == 12
    assert len(seen) == 7  # 0..6 processed


def test_laziness_infinite_callable_with_islice():
    # Infinite-like callable; only consumed part is computed
    x = -1
    def f():
        nonlocal x
        x += 1
        return x
    seq = stream(f, count=None, sentinel=None)
    seq = stream(f, count=10)
    picked = list(itertools.islice(seq, 5))
    assert picked == [0, 1, 2, 3, 4]


@pytest.mark.parametrize(
    "start,stop,op,expected",
    [
        (0, 5, partial(map, double), [0, 2, 4, 6, 8]),
        (0, 5, partial(filter, is_even), [0, 2, 4]),
        (1, 6, partial(map, square), [1, 4, 9, 16, 25]),
    ],
)
def test_pipeline_parametrized(start, stop, op, expected):
    assert list(pipeline(stream((start, stop)), op)) == expected
