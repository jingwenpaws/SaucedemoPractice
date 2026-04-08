from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from typing import TYPE_CHECKING

from src.constants.constants import PageUrl
from src.pages.base_page import BasePage
from src.utils.logger import Step

if TYPE_CHECKING:
    from src.pages.inventory_page import InventoryPage


class LoginPageLocators:
    """
    Locators for the Login Page elements.
    """
    USERNAME_FIELD = (By.CSS_SELECTOR, "#user-name")
    PASSWORD_FIELD = (By.CSS_SELECTOR, "#password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "#login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")


class LoginPage(BasePage):
    """
    Page Object for the Login Page, providing methods to authenticate users.
    """
    URL_PATH = PageUrl.LOGIN

    def is_at(self) -> bool:
        """
        Check if the browser is currently on the Login page.

        Returns:
            bool: True if both the URL matches and the username field is visible.
        """
        if not super().is_at():
            return False

        try:
            self.find_element(LoginPageLocators.USERNAME_FIELD)
            return True
        except TimeoutException:
            return False

    @Step("Attempt to login as '{username}'")
    def login(self, username: str, password: str, is_sensitive: bool = False) -> None:
        """
        Perform the base login UI actions (input credentials and click login)
        without expecting or returning a specific page transition.
        Ideal for negative testing where the user remains on the Login Page.

        Args:
            username: The username string to enter.
            password: The password string to enter.
            is_sensitive (bool): Whether to mask the key in logs. Defaults to False
        """
        self.send_keys(LoginPageLocators.USERNAME_FIELD, username)
        self.send_keys(LoginPageLocators.PASSWORD_FIELD, password, is_sensitive=is_sensitive)
        self.click(LoginPageLocators.LOGIN_BUTTON)

    @Step("Login as '{username}' and expect it to be successful")
    def login_success(self, username: str, password: str, is_sensitive: bool = True) -> "InventoryPage":
        """
        Perform a login action with valid credentials and transition to the Inventory Page.
        Ideal for happy path scenarios.

        Args:
            username: The username string to enter.
            password: The password string to enter.
            is_sensitive (bool): Whether to mask the key in logs. Defaults to True

        Returns:
            InventoryPage: The page object for the Inventory Page after a successful login.
        """
        self.login(username, password, is_sensitive=is_sensitive)
        from src.pages.inventory_page import InventoryPage
        return InventoryPage(self.driver)

    def get_error_message(self) -> str:
        """
        Retrieve the error message text displayed upon a failed login attempt.

        Returns:
            str: The text content of the error message element.
        """
        return self.find_element(LoginPageLocators.ERROR_MESSAGE).text