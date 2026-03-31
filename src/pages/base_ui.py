import logging
from abc import ABC
from typing import Tuple, Optional, List

from src.utils.config import Config
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

logger = logging.getLogger(__name__)
Locator = Tuple[str, str]

class BaseUI(ABC):
    def __init__(self, driver: WebDriver) -> None:
        """
        Initialize the BasePage with a WebDriver instance and configuration.

        Args:
            driver (WebDriver): The Selenium WebDriver instance.
        """
        self.driver = driver
        self.config = Config.get()
        self.wait = WebDriverWait(self.driver, self.config.driver.timeout)

    def click(self, locator: Locator, force: bool = False) -> None:
        """
        Wait for an element to be clickable and perform a click action.

        Args:
            locator (Locator): The locator for the element.
            force (bool): If True, use JavaScript click if a standard click is intercepted.

        Raises:
            ElementClickInterceptedException: If the click is blocked and force is False.
        """
        if force:
            logger.warning(f"Force click enabled for {locator}. Bypassing visibility check.")
            target = self.find_element(locator)
            self.driver.execute_script("arguments[0].click();", target)
            return
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except ElementClickInterceptedException:
            logger.error(f"Click intercepted for {locator} and 'force' is set to False.")
            raise

    def find_element(self, locator: Locator) -> WebElement:
        """
        Wait for an element to be visible on the DOM.

        Args:
            locator (Locator): The (By, Value) tuple for the element.

        Returns:
            WebElement: The Selenium WebElement once it becomes visible.

        Raises:
            TimeoutException: If the element is not visible within the timeout period.
        """
        try:
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            logger.error(f"Timeout: Element with locator {locator} not found or not visible.")
            raise

    def find_elements(self, locator: tuple) -> List[WebElement]:
        """
        Wait for elements to be present on the DOM.

        Args:
            locator (tuple): The (By, Value) tuple for the elements.

        Returns:
            List[WebElement]: A list of WebElements found. Returns an empty list
                              if no elements match the locator within the timeout.
        """
        try:
            return self.wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            logger.info(f"No elements found for locator {locator} within timeout.")
            return []

    def is_element_visible(self, locator: Locator, timeout: int = 3) -> bool:
        """
        Check if the element is visible.

        Args:
            locator (Locator): The (By, Value) tuple for the element.
            timeout: the timeout in seconds.
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            logger.debug(f"Element {locator} is not visible.")
            return False

    def wait_for_invisibility(self, locator: Locator, message: Optional[str] = None) -> bool:
        """
        Wait for an element to disappear or become hidden.

        Args:
            locator (Locator): The locator for the element.
            message (str, optional): Custom error message if timeout occurs.

        Returns:
            bool: True if the element is invisible.

        Raises:
            TimeoutException: If the element is still visible after the timeout.
        """
        try:
            return self.wait.until(EC.invisibility_of_element_located(locator))
        except TimeoutException as e:
            detailed_msg = message or f"Element {locator} is still visible after timeout."
            logger.error(detailed_msg)
            raise TimeoutException(detailed_msg) from e

    def send_keys(self, locator: Locator, text: str, clear: bool = True, is_sensitive: bool = False) -> None:
        """
        Send text input to an element after waiting for its visibility.

        Args:
            locator (Locator): The locator for the element.
            text (str): The string to enter into the element.
            clear (bool): Whether to clear the field before typing. Defaults to True.
            is_sensitive (bool): Whether to mask the key in logs. Defaults to False.
        """
        display_text = "********" if is_sensitive else text
        logger.info(f"Typing '{display_text}' into element: {locator}")
        element = self.find_element(locator)
        if clear:
            element.clear()
        element.send_keys(text)

    def scroll_to_element(self, locator: Locator) -> None:
        """
        Scroll the page until the specified element is in view.

        Args:
            locator (Locator): The locator for the element.
        """
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def select_dropdown_by_value(self, locator: tuple, value: str) -> None:
        """
        Wait for a dropdown element to be visible and select an option by its HTML 'value' attribute.

        Args:
            locator (tuple): The (By, Value) tuple for the dropdown element.
            value (str): The value attribute of the <option> to select.
        """
        element = self.find_element(locator)
        select_obj = Select(element)
        select_obj.select_by_value(value)

    def select_dropdown_by_text(self, locator: tuple, visible_text: str) -> None:
        """
        Wait for a dropdown element to be visible and select an option by its visible text.

        Args:
            locator (tuple): The (By, Value) tuple for the dropdown element.
            visible_text (str): The exact visible text of the <option> to select.
        """
        element = self.find_element(locator)
        select_obj = Select(element)
        select_obj.select_by_visible_text(visible_text)