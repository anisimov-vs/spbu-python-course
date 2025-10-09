## @file generators.py
## @brief Input data generators for lazy streaming pipelines.
## @details Provides various generator functions for creating input sequences.

from typing import Generator, Union, TypeVar, Callable

T = TypeVar("T")


def range_generator(start: int, stop: int, step: int = 1) -> Generator[int, None, None]:
    """
    Generate integers in a range.

    Args:
        start: Starting value (inclusive).
        stop: Ending value (exclusive).
        step: Step size (must be non-zero).

    Yields:
        Integers from start to stop with the given step, lazily.

    Raises:
        ValueError: If step is zero.

    Examples:
        >>> list(range_generator(0, 5))
        [0, 1, 2, 3, 4]
        >>> list(range_generator(10, 0, -2))
        [10, 8, 6, 4, 2]
    """
    if step == 0:
        raise ValueError("step cannot be zero")

    current = start
    if step > 0:
        while current < stop:
            yield current
            current += step
    else:
        while current > stop:
            yield current
            current += step


def sequence_generator(sequence: list[T]) -> Generator[T, None, None]:
    """
    Generate elements from a sequence.

    Args:
        sequence: Input list to iterate over.

    Yields:
        Elements of the input list one by one, lazily.

    Examples:
        >>> list(sequence_generator([1, 2, 3]))
        [1, 2, 3]
    """
    for item in sequence:
        yield item


def repeat_generator(
    value: T, times: Union[int, None] = None
) -> Generator[T, None, None]:
    """
    Generate a value repeatedly.

    Args:
        value: Value to repeat.
        times: Number of repetitions; if None, repeats infinitely.

    Yields:
        The value repeated either times times or infinitely if times is None.

    Raises:
        ValueError: If times is negative.

    Examples:
        >>> list(repeat_generator("x", 3))
        ['x', 'x', 'x']
        >>> gen = repeat_generator(1)  # infinite
        >>> next(gen), next(gen)
        (1, 1)
    """
    if times is None:
        while True:
            yield value
    else:
        if times < 0:
            raise ValueError("times cannot be negative")
        for _ in range(times):
            yield value


def custom_generator(
    func: Callable[[], Generator[T, None, None]]
) -> Generator[T, None, None]:
    """
    Create a generator from a custom function.

    Args:
        func: Function that returns a generator of T.

    Yields:
        Elements produced by the generator returned by func.

    Examples:
        >>> def gen():
        ...     yield 1
        ...     yield 2
        >>> list(custom_generator(gen))
        [1, 2]
    """
    yield from func()
