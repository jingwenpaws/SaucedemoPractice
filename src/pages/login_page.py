from selenium.webdriver.common.by import By

from src.pages.inventory_page import InventoryPage
from src.pages.base_page import BasePage


class LoginPageLocators:
    """
    Locators for the Login Page elements.
    """
    USERNAME_FIELD = (By.ID, "user-name")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")


class LoginPage(BasePage):
    """
    Page Object for the Login Page, providing methods to authenticate users.
    """
    URL_PATH = "/"

    def is_at(self) -> bool:
        """
        Check if the browser is currently on the Login page.

        Returns:
            bool: True if both the URL matches and the username field is visible.
        """
        is_url_correct = self.URL_PATH in self.driver.current_url
        is_element_visible = self.is_element_visible(LoginPageLocators.USERNAME_FIELD)

        return is_url_correct and is_element_visible

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

    def login_success(self, username: str, password: str, is_sensitive: bool = True) -> InventoryPage:
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
        return InventoryPage(self.driver)

    def get_error_message(self) -> str:
        """
        Retrieve the error message text displayed upon a failed login attempt.

        Returns:
            str: The text content of the error message element.
        """
        return self.find_element(LoginPageLocators.ERROR_MESSAGE).text