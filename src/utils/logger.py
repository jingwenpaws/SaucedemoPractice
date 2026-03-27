import logging
from functools import wraps
from typing import Any, Callable, Optional, Type
from types import TracebackType

import allure

logger = logging.getLogger(__name__)

class Step:
    """A custom context manager and decorator for test logging and Allure reporting.

    Attributes:
        title: A string representing the description of the test step or action.
    """

    def __init__(self, title: str) -> None:
        self.title = title
        self._allure_step = allure.step(title)

    def __enter__(self) -> "Step":
        logger.info("Step: %s", self.title)
        self._allure_step.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if exc_type:
            logger.error("Step failed: %s (Error: %s)", self.title, exc_val)
        self._allure_step.__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info("Action: %s", self.title)
            try:
                with self._allure_step:
                    return func(*args, **kwargs)
            except Exception as e:
                logger.error("Action failed: %s (Error: %s)", self.title, e)
                raise
        return wrapper