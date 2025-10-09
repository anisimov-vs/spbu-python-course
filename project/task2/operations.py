## @file operations.py
## @brief Pipeline operations for transforming and filtering data streams.
## @details Provides map, filter, compress, reduce and other stream operations.

from typing import Generator, Callable, TypeVar, Iterable, Tuple
from functools import reduce as functools_reduce

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def pipeline(source: Iterable[T]) -> Generator[T, None, None]:
    """
    Lazily yield items from a data source.

    Args:
        source: Input iterable to process.

    Yields:
        Elements from the source one by one.

    Examples:
        >>> from project.task2.generators import range_generator
        >>> list(pipeline(range_generator(0, 5)))
        [0, 1, 2, 3, 4]
    """
    yield from source


def map_op(func: Callable[[T], U]) -> Callable[[Iterable[T]], Generator[U, None, None]]:
    """
    Create a map operation that applies a function to each element lazily.

    Args:
        func: Function to apply to each element.

    Returns:
        Operation that transforms the input stream element-wise.

    Examples:
        >>> def double(x: int) -> int: return x * 2
        >>> list(map_op(double)(range(5)))
        [0, 2, 4, 6, 8]
    """

    def operation(iterable: Iterable[T]) -> Generator[U, None, None]:
        for item in iterable:
            yield func(item)

    return operation


def filter_op(
    predicate: Callable[[T], bool]
) -> Callable[[Iterable[T]], Generator[T, None, None]]:
    """
    Create a filter operation that keeps elements satisfying a predicate.

    Args:
        predicate: Function returning True for elements to keep.

    Returns:
        Operation that filters the input stream lazily.

    Examples:
        >>> def is_even(x: int) -> bool: return x % 2 == 0
        >>> list(filter_op(is_even)(range(6)))
        [0, 2, 4]
    """

    def operation(iterable: Iterable[T]) -> Generator[T, None, None]:
        for item in iterable:
            if predicate(item):
                yield item

    return operation


def compress_op(
    selectors: Iterable[bool | int],
) -> Callable[[Iterable[T]], Generator[T, None, None]]:
    """
    Create a compress operation using boolean/int selectors.

    Args:
        selectors: Boolean or int values indicating which elements to keep (truthy keeps).

    Returns:
        Operation that compresses the input stream based on selectors.

    Examples:
        >>> data = [1, 2, 3, 4, 5]
        >>> sels = [True, 0, 1, False, 1]
        >>> list(compress_op(sels)(data))
        [1, 3, 5]
    """

    def operation(iterable: Iterable[T]) -> Generator[T, None, None]:
        for item, selector in zip(iterable, selectors):
            if selector:
                yield item

    return operation


def take_op(n: int) -> Callable[[Iterable[T]], Generator[T, None, None]]:
    """
    Create a take operation that yields the first n elements.

    Args:
        n: Number of elements to take (must be non-negative).

    Returns:
        Operation that takes the first n elements lazily.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> list(take_op(3)(range(10)))
        [0, 1, 2]
    """
    if n < 0:
        raise ValueError("n cannot be negative")

    def operation(iterable: Iterable[T]) -> Generator[T, None, None]:
        count = 0
        for item in iterable:
            if count >= n:
                break
            yield item
            count += 1

    return operation


def drop_op(n: int) -> Callable[[Iterable[T]], Generator[T, None, None]]:
    """
    Create a drop operation that skips the first n elements.

    Args:
        n: Number of elements to drop (must be non-negative).

    Returns:
        Operation that drops the first n elements lazily.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> list(drop_op(3)(range(6)))
        [3, 4, 5]
    """
    if n < 0:
        raise ValueError("n cannot be negative")

    def operation(iterable: Iterable[T]) -> Generator[T, None, None]:
        iterator = iter(iterable)
        for _ in range(n):
            try:
                next(iterator)
            except StopIteration:
                return
        yield from iterator

    return operation


def take_while_op(
    predicate: Callable[[T], bool]
) -> Callable[[Iterable[T]], Generator[T, None, None]]:
    """
    Create a take_while operation that yields elements while predicate is true.

    Args:
        predicate: Function to test each element.

    Returns:
        Operation that yields items while the predicate holds.

    Examples:
        >>> def lt5(x: int) -> bool: return x < 5
        >>> list(take_while_op(lt5)(range(10)))
        [0, 1, 2, 3, 4]
    """

    def operation(iterable: Iterable[T]) -> Generator[T, None, None]:
        for item in iterable:
            if not predicate(item):
                break
            yield item

    return operation


def drop_while_op(
    predicate: Callable[[T], bool]
) -> Callable[[Iterable[T]], Generator[T, None, None]]:
    """
    Create a drop_while operation that skips elements while predicate is true.

    Args:
        predicate: Function to test each element.

    Returns:
        Operation that drops items while the predicate holds, then yields the rest.

    Examples:
        >>> def lt5(x: int) -> bool: return x < 5
        >>> list(drop_while_op(lt5)(range(10)))
        [5, 6, 7, 8, 9]
    """

    def operation(iterable: Iterable[T]) -> Generator[T, None, None]:
        iterator = iter(iterable)
        for item in iterator:
            if not predicate(item):
                yield item
                break
        yield from iterator

    return operation


def reduce_op(
    func: Callable[[U, T], U], initial: U
) -> Callable[[Iterable[T]], Generator[U, None, None]]:
    """
    Create a reduce operation that aggregates all elements into a single value.

    Args:
        func: Binary function combining accumulator and element.
        initial: Initial value for the reduction.

    Returns:
        Operation that yields exactly one reduced value.

    Examples:
        >>> def add(acc: int, x: int) -> int: return acc + x
        >>> list(reduce_op(add, 0)(range(5)))
        [10]
    """

    def operation(iterable: Iterable[T]) -> Generator[U, None, None]:
        result: U = functools_reduce(func, iterable, initial)
        yield result

    return operation


def zip2_op(
    other: Iterable[U],
) -> Callable[[Iterable[T]], Generator[Tuple[T, U], None, None]]:
    """
    Create a zip operation for two streams without using Any.

    Args:
        other: Second iterable to zip with the input stream.

    Returns:
        Operation that yields (left, right) tuples element-wise.

    Examples:
        >>> left = [1, 2, 3]
        >>> right = ["a", "b", "c"]
        >>> list(zip2_op(right)(left))
        [(1, 'a'), (2, 'b'), (3, 'c')]
    """

    def operation(iterable: Iterable[T]) -> Generator[Tuple[T, U], None, None]:
        for a, b in zip(iterable, other):
            yield (a, b)

    return operation


def zip3_op(
    other1: Iterable[U], other2: Iterable[V]
) -> Callable[[Iterable[T]], Generator[Tuple[T, U, V], None, None]]:
    """
    Create a zip operation for three streams without using Any.

    Args:
        other1: Second iterable to zip with the input stream.
        other2: Third iterable to zip with the input stream.

    Returns:
        Operation that yields (x, y, z) tuples element-wise.

    Examples:
        >>> a = [1, 2, 3]
        >>> b = ["a", "b", "c"]
        >>> c = [True, False, True]
        >>> list(zip3_op(b, c)(a))
        [(1, 'a', True), (2, 'b', False), (3, 'c', True)]
    """

    def operation(iterable: Iterable[T]) -> Generator[Tuple[T, U, V], None, None]:
        for t, u, v in zip(iterable, other1, other2):
            yield (t, u, v)

    return operation
