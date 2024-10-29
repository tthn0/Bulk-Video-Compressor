import time
from collections.abc import Callable
from functools import wraps
from logging import Logger
from typing import Any


def time_function(logger: Logger) -> Callable:
    """
    Parameterized decorator to time the execution of a function and log the time taken.

    Args:
        logger (Optional[logging.Logger]): The logger to use for logging. If not provided, it defaults to the root logger.

    Returns:
        Callable: The wrapped function with timing enabled.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(wrapped=func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time: float = time.perf_counter()
            result: Any = func(*args, **kwargs)
            end_time: float = time.perf_counter()
            elapsed_time: float = end_time - start_time
            logger.info(
                msg=f"Execution of '{func.__name__}' took {elapsed_time:.4f} seconds."
            )
            return result

        return wrapper

    return decorator
