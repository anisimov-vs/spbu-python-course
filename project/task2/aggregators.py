## @file aggregators.py
## @brief Aggregator functions for collecting pipeline results.
## @details Provides functions to materialize lazy generators into collections.

from typing import TypeVar, Iterable, Union

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def to_list(iterable: Iterable[T]) -> list[T]:
    """
    Collect all elements into a list.

    Args:
        iterable: Input iterable.

    Returns:
        List containing all elements in iteration order.

    Examples:
        >>> to_list(range(3))
        [0, 1, 2]
        >>> to_list(x for x in [1, 2, 3] if x > 1)
        [2, 3]
    """
    return list(iterable)


def to_set(iterable: Iterable[T]) -> set[T]:
    """
    Collect all elements into a set.

    Args:
        iterable: Input iterable.

    Returns:
        Set containing unique elements (order not guaranteed).

    Examples:
        >>> to_set([1, 2, 2, 3])
        {1, 2, 3}
        >>> to_set(range(3))
        {0, 1, 2}
    """
    return set(iterable)


def to_dict(iterable: Iterable[tuple[K, V]]) -> dict[K, V]:
    """
    Collect key-value pairs into a dictionary.

    Args:
        iterable: Iterable of (key, value) tuples.

    Returns:
        Dictionary constructed from the given pairs (later keys overwrite earlier ones).

    Examples:
        >>> to_dict([("a", 1), ("b", 2)])
        {'a': 1, 'b': 2}
        >>> to_dict([("x", 1), ("x", 3)])
        {'x': 3}
    """
    return dict(iterable)


def count(iterable: Iterable[T]) -> int:
    """
    Count the number of elements.

    Args:
        iterable: Input iterable.

    Returns:
        Number of elements in the iterable.

    Examples:
        >>> count(range(5))
        5
        >>> count(x for x in [1, 2, 3] if x > 1)
        2
    """
    return sum(1 for _ in iterable)


def sum_all(iterable: Iterable[Union[int, float]]) -> float:
    """
    Sum all numeric elements.

    Args:
        iterable: Iterable of numbers.

    Returns:
        Sum of all elements as float.

    Examples:
        >>> sum_all([1, 2, 3])
        6.0
        >>> sum_all((0.5, 1.5))
        2.0
    """
    total: float = 0.0
    for x in iterable:
        total += float(x)
    return total


def product_all(iterable: Iterable[Union[int, float]]) -> Union[int, float]:
    """
    Compute product of all numeric elements.

    Args:
        iterable: Iterable of numbers.

    Returns:
        Product of all elements (int if inputs are ints and no float encountered, otherwise float).

    Raises:
        ValueError: If iterable is empty.

    Examples:
        >>> product_all([2, 3, 4])
        24
        >>> product_all([1.5, 2])
        3.0
    """
    result: Union[int, float] = 1
    has_items: bool = False
    for x in iterable:
        has_items = True
        result = result * x
    if not has_items:
        raise ValueError("Cannot compute product of empty iterable")
    return result


def min_value(iterable: Iterable[int]) -> int:
    """
    Find minimum element.

    Args:
        iterable: Input iterable of integers.

    Returns:
        Minimum element of the iterable.

    Raises:
        ValueError: If iterable is empty.

    Examples:
        >>> min_value([5, 2, 8, 1, 9])
        1
        >>> min_value(range(3))
        0
    """
    iterator = iter(iterable)
    try:
        min_item: int = next(iterator)
    except StopIteration:
        raise ValueError("min_value() arg is an empty sequence")
    for item in iterator:
        if item < min_item:
            min_item = item
    return min_item


def max_value(iterable: Iterable[int]) -> int:
    """
    Find maximum element.

    Args:
        iterable: Input iterable of integers.

    Returns:
        Maximum element of the iterable.

    Raises:
        ValueError: If iterable is empty.

    Examples:
        >>> max_value([5, 2, 8, 1, 9])
        9
        >>> max_value(range(3))
        2
    """
    iterator = iter(iterable)
    try:
        max_item: int = next(iterator)
    except StopIteration:
        raise ValueError("max_value() arg is an empty sequence")
    for item in iterator:
        if item > max_item:
            max_item = item
    return max_item


def first(iterable: Iterable[T]) -> T:
    """
    Get the first element.

    Args:
        iterable: Input iterable.

    Returns:
        First element of the iterable.

    Raises:
        ValueError: If iterable is empty.

    Examples:
        >>> first([10, 20, 30])
        10
        >>> first(x for x in [1, 2, 3] if x > 1)
        2
    """
    for item in iterable:
        return item
    raise ValueError("Cannot get first element of empty iterable")


def last(iterable: Iterable[T]) -> T:
    """
    Get the last element.

    Args:
        iterable: Input iterable.

    Returns:
        Last element of the iterable.

    Raises:
        ValueError: If iterable is empty.

    Examples:
        >>> last([10, 20, 30])
        30
        >>> last(range(1))
        0
    """
    iterator = iter(iterable)
    try:
        last_item: T = next(iterator)
    except StopIteration:
        raise ValueError("Cannot get last element of empty iterable")
    for item in iterator:
        last_item = item
    return last_item
