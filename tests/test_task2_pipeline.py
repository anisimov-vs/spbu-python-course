# tests/test_task2_pipeline.py

import pytest
from typing import Generator

from project.task2.generators import (
    range_generator,
    sequence_generator,
    repeat_generator,
    custom_generator,
)
from project.task2.operations import (
    pipeline,
    map_op,
    filter_op,
    compress_op,
    take_op,
    drop_op,
    reduce_op,
    take_while_op,
    drop_while_op,
)
from project.task2.aggregators import (
    to_list,
    to_set,
    to_dict,
    count,
    sum_all,
    product_all,
    min_value,
    max_value,
    first,
    last,
)


# Test Generators
def test_range_generator_basic() -> None:
    result = to_list(range_generator(0, 5))
    assert result == [0, 1, 2, 3, 4]


def test_range_generator_with_step() -> None:
    result = to_list(range_generator(0, 10, 2))
    assert result == [0, 2, 4, 6, 8]


def test_range_generator_negative_step() -> None:
    result = to_list(range_generator(10, 0, -2))
    assert result == [10, 8, 6, 4, 2]


def test_range_generator_zero_step_raises() -> None:
    with pytest.raises(ValueError):
        to_list(range_generator(0, 5, 0))


def test_sequence_generator() -> None:
    result = to_list(sequence_generator([1, 2, 3, 4]))
    assert result == [1, 2, 3, 4]


def test_repeat_generator_finite() -> None:
    result = to_list(repeat_generator("x", 3))
    assert result == ["x", "x", "x"]


def test_repeat_generator_infinite() -> None:
    gen = repeat_generator(5, None)
    result = to_list(take_op(5)(gen))
    assert result == [5, 5, 5, 5, 5]


def test_repeat_generator_negative_times_raises() -> None:
    with pytest.raises(ValueError):
        to_list(repeat_generator(1, -1))


def test_custom_generator() -> None:
    def my_gen() -> Generator[int, None, None]:
        yield 1
        yield 2
        yield 3

    result = to_list(custom_generator(my_gen))
    assert result == [1, 2, 3]


# Test Operations
def test_map_op_basic() -> None:
    def double(x: int) -> int:
        return x * 2

    result = to_list(map_op(double)(range(5)))
    assert result == [0, 2, 4, 6, 8]


def test_filter_op_basic() -> None:
    def is_even(x: int) -> bool:
        return x % 2 == 0

    result = to_list(filter_op(is_even)(range(10)))
    assert result == [0, 2, 4, 6, 8]


def test_compress_op_basic() -> None:
    data = [1, 2, 3, 4, 5]
    selectors = [True, False, True, False, True]
    result = to_list(compress_op(selectors)(data))
    assert result == [1, 3, 5]


def test_compress_op_with_ints() -> None:
    data = ["a", "b", "c", "d"]
    selectors = [1, 0, 1, 1]
    result = to_list(compress_op(selectors)(data))
    assert result == ["a", "c", "d"]


def test_take_op_basic() -> None:
    result = to_list(take_op(3)(range(10)))
    assert result == [0, 1, 2]


def test_take_op_more_than_available() -> None:
    result = to_list(take_op(10)(range(5)))
    assert result == [0, 1, 2, 3, 4]


def test_take_op_negative_raises() -> None:
    with pytest.raises(ValueError):
        take_op(-1)


def test_drop_op_basic() -> None:
    result = to_list(drop_op(3)(range(6)))
    assert result == [3, 4, 5]


def test_drop_op_more_than_available() -> None:
    result = to_list(drop_op(10)(range(5)))
    assert result == []


def test_drop_op_negative_raises() -> None:
    with pytest.raises(ValueError):
        drop_op(-1)


def test_take_while_op_basic() -> None:
    def less_than_five(x: int) -> bool:
        return x < 5

    result = to_list(take_while_op(less_than_five)(range(10)))
    assert result == [0, 1, 2, 3, 4]


def test_drop_while_op_basic() -> None:
    def less_than_five(x: int) -> bool:
        return x < 5

    result = to_list(drop_while_op(less_than_five)(range(10)))
    assert result == [5, 6, 7, 8, 9]


def test_reduce_op_sum() -> None:
    def add(acc: int, x: int) -> int:
        return acc + x

    result = to_list(reduce_op(add, 0)(range(5)))
    assert result == [10]


def test_reduce_op_product() -> None:
    def multiply(acc: int, x: int) -> int:
        return acc * x

    result = to_list(reduce_op(multiply, 1)(range(1, 5)))
    assert result == [24]


# Test Pipeline - chain operations directly without pipeline() for complex cases
def test_pipeline_simple() -> None:
    result = to_list(pipeline(range_generator(0, 10)))
    assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_pipeline_with_map() -> None:
    def double(x: int) -> int:
        return x * 2

    gen = range_generator(0, 10)
    mapped = map_op(double)(gen)
    result = to_list(mapped)
    assert result == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


def test_pipeline_chained() -> None:
    def double(x: int) -> int:
        return x * 2

    def greater_than_five(x: int) -> bool:
        return x > 5

    def increment(x: int) -> int:
        return x + 1

    gen = range_generator(0, 10)
    mapped1 = map_op(double)(gen)
    filtered = filter_op(greater_than_five)(mapped1)
    mapped2 = map_op(increment)(filtered)
    result = to_list(mapped2)
    assert result == [7, 9, 11, 13, 15, 17, 19]


def test_pipeline_complex() -> None:
    def square(x: int) -> int:
        return x**2

    def is_even(x: int) -> bool:
        return x % 2 == 0

    gen = range_generator(1, 11)
    mapped = map_op(square)(gen)
    filtered = filter_op(is_even)(mapped)
    taken = take_op(3)(filtered)
    result = to_list(taken)
    assert result == [4, 16, 36]


def test_pipeline_with_drop() -> None:
    def times_ten(x: int) -> int:
        return x * 10

    gen = range_generator(0, 10)
    dropped = drop_op(5)(gen)
    mapped = map_op(times_ten)(dropped)
    result = to_list(mapped)
    assert result == [50, 60, 70, 80, 90]


def test_pipeline_with_compress() -> None:
    gen = sequence_generator([10, 20, 30, 40, 50])
    compressed = compress_op([True, False, True, True, False])(gen)
    result = to_list(compressed)
    assert result == [10, 30, 40]


def test_pipeline_empty() -> None:
    result = to_list(pipeline(range_generator(0, 0)))
    assert result == []


# Test Aggregators
def test_to_list_aggregator() -> None:
    result = to_list(range(5))
    assert result == [0, 1, 2, 3, 4]


def test_to_set_aggregator() -> None:
    result = to_set([1, 2, 2, 3, 3, 3])
    assert result == {1, 2, 3}


def test_to_dict_aggregator() -> None:
    result = to_dict([("a", 1), ("b", 2), ("c", 3)])
    assert result == {"a": 1, "b": 2, "c": 3}


def test_count_aggregator() -> None:
    result = count(range(10))
    assert result == 10


def test_sum_all_aggregator() -> None:
    result = sum_all([1, 2, 3, 4, 5])
    assert result == 15.0


def test_product_all_aggregator() -> None:
    result = product_all([2, 3, 4])
    assert result == 24


def test_product_all_empty_raises() -> None:
    with pytest.raises(ValueError):
        product_all([])


def test_min_value_aggregator() -> None:
    result = min_value([5, 2, 8, 1, 9])
    assert result == 1


def test_min_value_empty_raises() -> None:
    with pytest.raises(ValueError):
        min_value([])


def test_max_value_aggregator() -> None:
    result = max_value([5, 2, 8, 1, 9])
    assert result == 9


def test_max_value_empty_raises() -> None:
    with pytest.raises(ValueError):
        max_value([])


def test_first_aggregator() -> None:
    result = first(range(5))
    assert result == 0


def test_first_empty_raises() -> None:
    with pytest.raises(ValueError):
        first([])


def test_last_aggregator() -> None:
    result = last(range(5))
    assert result == 4


def test_last_empty_raises() -> None:
    with pytest.raises(ValueError):
        last([])


# Integration Tests
def test_full_pipeline_integration() -> None:
    """Test a complete pipeline with multiple operations and aggregation."""

    def is_even(x: int) -> bool:
        return x % 2 == 0

    def half(x: int) -> int:
        return x // 2

    gen = range_generator(1, 101)
    filtered = filter_op(is_even)(gen)
    mapped = map_op(half)(filtered)
    taken = take_op(10)(mapped)
    result = sum_all(taken)
    assert result == 55.0


def test_pipeline_with_custom_function() -> None:
    """Test pipeline with custom transformation."""

    def square_if_even(x: int) -> int:
        return x**2 if x % 2 == 0 else x

    gen = range_generator(1, 6)
    mapped = map_op(square_if_even)(gen)
    result = to_list(mapped)
    assert result == [1, 4, 3, 16, 5]


def test_lazy_evaluation() -> None:
    """Test that pipeline is truly lazy."""
    call_count = 0

    def counting_mapper(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    gen = range_generator(0, 100)
    taken = take_op(3)(gen)
    mapped = map_op(counting_mapper)(taken)
    result = to_list(mapped)

    assert result == [0, 2, 4]
    assert call_count == 3


def test_pipeline_type_transformations() -> None:
    """Test pipeline with multiple type transformations."""

    def double(x: int) -> int:
        return x * 2

    def to_str(x: int) -> str:
        return str(x)

    def format_num(s: str) -> str:
        return f"num_{s}"

    gen = range_generator(1, 6)
    mapped1 = map_op(double)(gen)
    mapped2 = map_op(to_str)(mapped1)
    mapped3 = map_op(format_num)(mapped2)
    result = to_list(mapped3)
    assert result == ["num_2", "num_4", "num_6", "num_8", "num_10"]


@pytest.mark.parametrize(
    "n,expected",
    [
        (5, [0, 1, 2, 3, 4]),
        (1, [0]),
        (0, []),
    ],
)
def test_pipeline_parametrized(n: int, expected: list[int]) -> None:
    """Parametrized test for different pipeline lengths."""
    gen = range_generator(0, 10)
    taken = take_op(n)(gen)
    result = to_list(taken)
    assert result == expected
