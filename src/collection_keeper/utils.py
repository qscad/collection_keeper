"""Misc tools."""
from typing import Any, Callable, Tuple


def safe_call(func: Callable) -> Callable:
    """Decorator to catch exceptions."""

    def safe_func(*args, **kwargs) -> Tuple[Any, str]:  # noqa: ANN002, ANN003
        try:
            return func(*args, **kwargs), ""
        except Exception as e:  # noqa: BLE001
            return None, str(e)

    return safe_func
