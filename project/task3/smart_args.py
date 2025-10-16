## @file smart_args.py
## @brief Smart argument handling with Isolated and Evaluated parameters.

import functools
import inspect
import copy
from typing import Callable, Optional, Any, TypeVar, cast, overload, ParamSpec


P = ParamSpec("P")
R = TypeVar("R")


class Isolated:
    """
    Marker class for parameters requiring deep copy on every call.

    When used as a default value with @smart_args decorator, ensures that
    the actual argument passed is deep-copied before use, preventing
    unintended mutations of mutable default arguments.

    If no argument is provided, raises TypeError requiring the argument.

    Example:
        >>> @smart_args
        ... def append_to_list(*, items: list = Isolated()):
        ...     items.append(1)
        ...     return items
        >>> original = [0]
        >>> result = append_to_list(items=original)
        >>> # original remains [0], result is [0, 1]
    """

    pass


class Evaluated:
    """
    Wrapper for lazy evaluation of default parameter values.

    When used as a default value with @smart_args decorator, the wrapped
    function is called each time the parameter is not provided, allowing
    for dynamic default values.

    Attributes:
        func: A callable that returns the default value.

    Args:
        func: A callable with no arguments that produces the default value.

    Raises:
        TypeError: If func is not callable.

    Example:
        >>> import random
        >>> @smart_args
        ... def get_value(*, value: int = Evaluated(lambda: random.randint(1, 100))):
        ...     return value
        >>> # Each call without 'value' generates a new random number
    """

    def __init__(self, func: Callable[[], Any]):
        """
        Initialize Evaluated with a callable.

        Args:
            func: A callable that takes no arguments and returns a value.

        Raises:
            TypeError: If func is not callable.
        """
        if not callable(func):
            raise TypeError("Evaluated must be initialized with a callable function.")
        self.func = func


@overload
def smart_args(func: Callable[P, R]) -> Callable[P, R]:
    ...


@overload
def smart_args(
    func: None = None, *, positional_support: bool = False
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def smart_args(
    func: Optional[Callable[P, R]] = None, *, positional_support: bool = False
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that enables special default argument handling with Isolated and Evaluated.

    This decorator processes function parameters with special default values:
    - Isolated(): Requires argument to be provided; if provided, creates a deep copy
    - Evaluated(callable): Calls the callable each time the parameter is not provided

    Args:
        func: The function to decorate. If None, returns a decorator.
        positional_support: If True, allows Isolated/Evaluated for positional parameters.
                          If False (default), only keyword-only parameters are allowed.

    Returns:
        The decorated function or a decorator function if func is None.

    Raises:
        AssertionError: If Isolated/Evaluated are used on positional parameters without
                       positional_support=True, or if Isolated and Evaluated are combined.
        TypeError: If a parameter with Isolated() default is not provided.

    Example:
        >>> @smart_args
        ... def process(*, data: dict = Isolated(), count: int = Evaluated(lambda: 0)):
        ...     data['count'] = count
        ...     return data
        >>> original = {}
        >>> result = process(data=original)
        >>> # original remains empty, result has {'count': 0}

    Note:
        - Isolated and Evaluated cannot be combined in the same parameter
        - Evaluated cannot return an Isolated instance
        - By default, special defaults work only with keyword-only parameters
    """

    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        """
        Actual decorator that wraps the function.

        Args:
            f: The function to wrap with smart argument handling.

        Returns:
            The wrapped function with special default argument behavior.
        """
        sig = inspect.signature(f)
        for name, param in sig.parameters.items():
            default_val = param.default
            is_isolated = isinstance(default_val, Isolated)
            is_evaluated = isinstance(default_val, Evaluated)

            assert not (
                is_isolated and is_evaluated
            ), "Cannot combine Isolated and Evaluated."

            if is_evaluated and (default_val.func is Isolated):
                raise AssertionError("Cannot combine Isolated and Evaluated.")

            if not positional_support and (is_isolated or is_evaluated):
                assert param.kind == inspect.Parameter.KEYWORD_ONLY

        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """
            Wrapper that processes special default arguments.

            Args:
                *args: Positional arguments for the function.
                **kwargs: Keyword arguments for the function.

            Returns:
                The result of calling the original function with processed arguments.

            Raises:
                TypeError: If a required Isolated parameter is not provided.
                AssertionError: If Evaluated returns an Isolated instance.
            """
            user_provided_args = sig.bind_partial(*args, **kwargs).arguments
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for name, value in bound_args.arguments.items():
                param = sig.parameters.get(name)
                if param is None:
                    continue

                if name not in user_provided_args and isinstance(value, Evaluated):
                    result = value.func()
                    if isinstance(result, Isolated):
                        raise AssertionError("Cannot combine Isolated and Evaluated.")
                    bound_args.arguments[name] = result

                if isinstance(param.default, Isolated):
                    if name not in user_provided_args:
                        raise TypeError(f"Missing required argument: '{name}'")
                    bound_args.arguments[name] = copy.deepcopy(value)

            return f(*bound_args.args, **bound_args.kwargs)

        return cast(Callable[P, R], wrapper)

    if func:
        return decorator(func)
    else:
        return decorator
