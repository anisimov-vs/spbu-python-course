## @file pipeline.py
## @brief Unified lazy stream, pipeline composition, and aggregation utilities.

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import Literal, Optional, TypeVar, cast, overload

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")

_MISSING = object()


@overload
def stream(
    source: Callable[[], T],
    *,
    count: int,
    sentinel: object = _MISSING,
    dict_mode: str = "keys",
) -> Iterator[T]:
    ...


@overload
def stream(
    source: Callable[[], T],
    *,
    count: None = None,
    sentinel: object,
    dict_mode: str = "keys",
) -> Iterator[T]:
    ...


@overload
def stream(
    source: Mapping[K, V],
    *,
    count: int | None = None,
    sentinel: object = _MISSING,
    dict_mode: Literal["keys"] = "keys",
) -> Iterator[K]:
    ...


@overload
def stream(
    source: Mapping[K, V],
    *,
    count: int | None = None,
    sentinel: object = _MISSING,
    dict_mode: Literal["values"],
) -> Iterator[V]:
    ...


@overload
def stream(
    source: Mapping[K, V],
    *,
    count: int | None = None,
    sentinel: object = _MISSING,
    dict_mode: Literal["items"],
) -> Iterator[tuple[K, V]]:
    ...


@overload
def stream(
    source: Iterable[T],
    *,
    count: int | None = None,
    sentinel: object = _MISSING,
    dict_mode: str = "keys",
) -> Iterator[T]:
    ...


def stream(
    source: object,
    *,
    count: int | None = None,
    sentinel: object = _MISSING,
    dict_mode: str = "keys",
) -> Iterator[object]:
    """
    Create a lazy stream from diverse source types.

    Supported sources:
    - Iterable (lists, tuples, sets, strings, generators): yields elements lazily
    - Mapping (dict): yields by dict_mode='keys' | 'values' | 'items'
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
    # callable -> repeated calls, controlled by count or sentinel
    if callable(source):
        callable_source = cast(Callable[[], object], source)
        if count is None and sentinel is _MISSING:
            raise ValueError("callable source requires 'count' or 'sentinel'")
        if count is not None:
            for _ in range(count):
                yield callable_source()
            return
        # sentinel mode
        while True:
            value = callable_source()
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
        "Unsupported source type for stream(); provide an iterable, mapping, "
        "or callable with count/sentinel."
    )


def pipeline(
    source: Iterable[T], *operations: Callable[[Iterable[object]], Iterable[object]]
) -> Iterable[object]:
    """
    Lazily apply a sequence of operations to a source.

    Each operation must accept an iterable and return an iterable (e.g., map, filter, zip via lambda).
    """
    result: Iterable[object] = source
    for op in operations:
        result = op(result)
    return result


@overload
def aggregate(iterable: Iterable[T]) -> list[T]:
    ...


@overload
def aggregate(iterable: Iterable[T], collector: Callable[[Iterable[T]], U]) -> U:
    ...


def aggregate(
    iterable: Iterable[T], collector: Optional[Callable[[Iterable[T]], object]] = None
) -> object:
    """
    Collect a lazy stream into a concrete collection using the provided collector.
    """
    if collector is None:
        return list(iterable)
    return collector(iterable)
