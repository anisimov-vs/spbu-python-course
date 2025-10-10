## @file pipeline.py
## @brief Unified lazy stream, pipeline composition, and aggregation utilities.

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from functools import reduce
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")

_MISSING = object()


def stream(
    source: Any,
    *,
    count: int | None = None,
    sentinel: Any = _MISSING,
    dict_mode: str = "keys",
) -> Iterator[Any]:
    """
    Create a lazy stream from diverse source types.

    Supported sources:
    - Iterable (lists, tuples, sets, strings, generators): yields elements lazily
    - Mapping (dict): yields by dict_mode='keys' | 'values' | 'items'
    - slice: interpreted as a numeric range, e.g., slice(0, 5, 2) -> 0,2,4
    - callable: repeatedly call the function
        * if count is provided: call exactly count times
        * if sentinel is provided: call until result == sentinel

    Args:
        source: Diverse input describing a lazy stream.
        count: Number of calls for callable sources.
        sentinel: Stop value for callable sources, stop when f() == sentinel.
        dict_mode: For mappings choose 'keys' | 'values' | 'items'.

    Yields:
        Lazy sequence of elements derived from source.
    """
    # slice -> numeric range
    if isinstance(source, slice):
        start = 0 if source.start is None else source.start
        stop = source.stop
        step = 1 if source.step is None else source.step
        if stop is None:
            raise ValueError("slice.stop must be provided for finite range")
        yield from range(start, stop, step)
        return

    # callable -> repeated calls, controlled by count or sentinel
    if callable(source):
        if count is None and sentinel is _MISSING:
            raise ValueError("callable source requires 'count' or 'sentinel'")
        if count is not None:
            for _ in range(count):
                yield source()
            return
        # sentinel mode
        while True:
            value = source()
            if value == sentinel:
                break
            yield value
        return

    # mapping -> choose view
    if isinstance(source, Mapping):
        if dict_mode == "keys":
            yield from source.keys()
        elif dict_mode == "values":
            yield from source.values()
        elif dict_mode == "items":
            yield from source.items()
        else:
            raise ValueError("dict_mode must be 'keys', 'values', or 'items'")
        return

    # general iterable
    if isinstance(source, Iterable):
        yield from source
        return

    raise TypeError(
        "Unsupported source type for stream(); provide an iterable, mapping, slice, "
        "numeric tuple/list, or callable with count/sentinel."
    )


def pipeline(source: Iterable[T], *operations: Callable[[Iterable], Iterable]) -> Iterable:
    """
    Lazily apply a sequence of operations to a source.

    Each operation must accept an iterable and return an iterable (e.g., map, filter, zip via lambda).
    """
    return reduce(lambda data, op: op(data), operations, source)


def aggregate(iterable: Iterable[T], collector: Callable[[Iterable[T]], Any] = list) -> Any:
    """
    Collect a lazy stream into a concrete collection using the provided collector.
    """
    return collector(iterable)
