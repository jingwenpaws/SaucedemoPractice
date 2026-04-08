from abc import abstractmethod

from src.pages.base_ui import BaseUI
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


class BasePage(BaseUI):
    """
    Abstract Base Page class that provides common functionality for all Page Objects.

    Attributes:
        driver (WebDriver): The Selenium WebDriver instance.
        config (MapObject): Configuration object containing environment settings.
        base_url (str): The root URL of the application.
        wait (WebDriverWait): Explicit wait instance for synchronization.
    """

    def __init__(self, driver: WebDriver) -> None:
        """
        Initialize the BasePage with a WebDriver instance and configuration.

        Args:
            driver (WebDriver): The Selenium WebDriver instance.
        """
        super().__init__(driver)
        self.base_url = self.config.BASE_URL

    @property
    @abstractmethod
    def URL_PATH(self) -> str:
        """
        Abstract property: Subclasses must define the relative URL path.

        Returns:
            str: The relative path to be appended to the base URL.
        """
        pass

    def load(self) -> "BasePage":
        """
        Navigate to the full URL composed of the base URL and the URL_PATH.

        Returns:
            BasePage: The current page instance for method chaining.
        """
        full_url = f"{self.base_url.rstrip('/')}/{self.URL_PATH.lstrip('/')}"
        self.logger.info(f"Navigating to: {full_url}")
        self.driver.get(full_url)
        return self

    def is_at(self) -> bool:
        """
        Check if the current browser URL contains the expected URL_PATH.

        Returns:
            bool: True if the current URL matches the expected path, False otherwise.
        """
        url_matches = self.wait_for_url_contains(self.URL_PATH)
        if not url_matches:
            return False

        try:
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except Exception as e:
            self.logger.warning(f"Page load not complete within timeout: {e}", stacklevel=2)
            return False

    def verify(self) -> "BasePage":
        """
        Verify that the browser is currently on the expected page.

        Returns:
            BasePage: The current page instance if verification passes.

        Raises:
            AssertionError: If the browser is not at the expected URL path.
        """
        assert self.is_at(), (
            f"Page verification failed. Current URL '{self.driver.current_url}' "
            f"does not contain expected path '{self.URL_PATH}'"
        )
        self.logger.info(f"Successfully verified location: {self.__class__.__name__}")
        return self

    def get_title(self) -> str:
        """
        Retrieve the current page title.

        Returns:
            str: The page title.
        """
        return self.driver.title

    def get_current_url(self) -> str:
        """
        Retrieve the current browser URL.

        Returns:
            str: The current URL.
        """
        return self.driver.current_url