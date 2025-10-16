## @file carry.py
## @brief Currying and uncurrying functions and LRU caching with configurable capacity.

import functools
from collections import OrderedDict
from typing import Callable, Any


def curry_explicit(function: Callable[..., Any], arity: int) -> Callable[..., Any]:
    """
    Transform a function to accept arguments one at a time (currying).
    
    Args:
        function: The function to curry. Can accept any number of arguments.
        arity: The number of arguments the function expects. Must be a non-negative integer.
    
    Returns:
        A curried version of the function that accepts arguments one at a time.
        When all arguments are provided, the original function is called.
    
    Raises:
        ValueError: If arity is not a non-negative integer.
        TypeError: If too many arguments are provided when calling the curried function.
    
    Example:
        >>> def add(x, y, z):
        ...     return x + y + z
        >>> curried_add = curry_explicit(add, 3)
        >>> result = curried_add(1)(2)(3)
        >>> print(result)
        6
    """
    if not isinstance(arity, int) or arity < 0:
        raise ValueError("Arity must be a non-negative integer.")
    
    def curry_wrapper(args_so_far: list[Any]) -> Callable[..., Any]:
        """
        Internal wrapper that accumulates arguments.
        
        Args:
            args_so_far: List of arguments collected so far.
        
        Returns:
            A function that accepts the next argument or the final result.
        """
        def inner_wrapper(new_arg: Any) -> Any:
            """
            Accept a single argument and determine next step.
            
            Args:
                new_arg: The next argument to add to the collection.
            
            Returns:
                Either another curried function or the final result.
            """
            all_args = args_so_far + [new_arg]
            if len(all_args) < arity:
                return curry_wrapper(all_args)
            else:
                return function(*all_args)
        return inner_wrapper
    
    if arity == 0:
        return lambda: function()
    return curry_wrapper([])


def uncurry_explicit(curried_function: Callable[..., Any], arity: int) -> Callable[..., Any]:
    """
    Transform a curried function back to accept all arguments at once.
    
    Args:
        curried_function: A curried function that accepts arguments one at a time.
        arity: The total number of arguments the original function expects.
    
    Returns:
        An uncurried function that accepts all arguments at once.
    
    Raises:
        ValueError: If arity is not a non-negative integer.
        TypeError: If the number of arguments provided doesn't match arity.
    
    Example:
        >>> def add(x, y, z):
        ...     return x + y + z
        >>> curried = curry_explicit(add, 3)
        >>> uncurried = uncurry_explicit(curried, 3)
        >>> result = uncurried(1, 2, 3)
        >>> print(result)
        6
    """
    if not isinstance(arity, int) or arity < 0:
        raise ValueError("Arity must be a non-negative integer.")
    
    def uncurried_wrapper(*args: Any) -> Any:
        """
        Accept all arguments at once and apply them sequentially.
        
        Args:
            *args: All arguments to pass to the curried function.
        
        Returns:
            The result of calling the curried function with all arguments.
        
        Raises:
            TypeError: If argument count doesn't match arity.
        """
        if len(args) != arity:
            raise TypeError(f"Expected {arity} arguments, but got {len(args)}.")
        if arity == 0:
            return curried_function()
        result = curried_function
        for arg in args:
            result = result(arg)
        return result
    
    return uncurried_wrapper


def cache(capacity: int = 0) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Create a decorator that caches function results with LRU eviction policy.
    
    Args:
        capacity: Maximum number of cached results. If 0 or negative, caching is disabled.
                 Defaults to 0 (disabled).
    
    Returns:
        A decorator function that adds caching to the decorated function.
    
    Example:
        >>> @cache(capacity=100)
        ... def expensive_computation(x):
        ...     return x ** 2
        >>> result = expensive_computation(5)  # Computed
        >>> result = expensive_computation(5)  # Retrieved from cache
    
    Note:
        - Functions with unhashable arguments (like lists or dicts) bypass the cache
        - Exceptions are not cached
        - Keyword argument order doesn't matter for cache keys
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorate a function with caching capability.
        
        Args:
            func: The function to decorate with caching.
        
        Returns:
            A wrapped version of the function with caching enabled.
        """
        if capacity <= 0:
            return func
        
        lru_cache: OrderedDict[Any, Any] = OrderedDict()
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper that implements caching logic.
            
            Args:
                *args: Positional arguments for the function.
                **kwargs: Keyword arguments for the function.
            
            Returns:
                The result of the function call, either from cache or newly computed.
            """
            try:
                key = (args, tuple(sorted(kwargs.items())))
                hash(key)
            except TypeError:
                return func(*args, **kwargs)
            
            if key in lru_cache:
                lru_cache.move_to_end(key)
                return lru_cache[key]
            
            try:
                result = func(*args, **kwargs)
            except Exception:
                raise
            
            if len(lru_cache) >= capacity:
                lru_cache.popitem(last=False)
            lru_cache[key] = result
            return result
        
        return wrapper
    return decorator