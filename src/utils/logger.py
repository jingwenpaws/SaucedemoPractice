import inspect
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
        self.width = 70

    def __enter__(self) -> "Step":
        banner = "═" * self.width
        logger.info(banner)
        logger.info(f"STEP: {self.title}")
        logger.info(banner)
        self._allure_step.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if exc_type:
            err_banner = "!" * self.width
            logger.error(err_banner)
            logger.error(f"STEP FAILED: {self.title}")
            logger.error(f"Reason: {exc_val}")
            logger.error(err_banner)
        else:
            logger.info(f"*** STEP SUCCESSFUL: {self.title} ***")
        self._allure_step.__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            try:
                dynamic_title = self.title.format(**bound_args.arguments)
            except KeyError:
                dynamic_title = self.title

            logger.info("Action: %s", dynamic_title)

            try:
                with allure.step(dynamic_title):
                    return func(*args, **kwargs)
            except Exception as e:
                logger.error("Action failed: %s (Error: %s)", dynamic_title, e)
                raise

        return wrapper
