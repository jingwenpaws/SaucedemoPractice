"""Tests for authentication and security."""
import pytest
import allure
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict, Any, Callable

from src.pages.inventory_page import InventoryPage
from src.pages.product_detail_page import ProductDetailPage
from src.pages.login_page import LoginPage
from src.utils.data_helper import load_json
from src.utils.config import MapObject
from src.utils.logger import Step

ACCESS_DENIED_TEMPLATE = "Epic sadface: You can only access '{path}' when you are logged in."
LOGIN_REQUIRED_INVENTORY_MSG = ACCESS_DENIED_TEMPLATE.format(
    path=InventoryPage.URL_PATH
)
LOGIN_REQUIRED_ITEM_MSG = ACCESS_DENIED_TEMPLATE.format(
    path=ProductDetailPage.URL_PATH
)

# Load test data globally for parametrization
_LOGIN_DATA = load_json("login_data.json")
NEG_CASES = _LOGIN_DATA["negative_test_users"]
NEG_IDS = [c["id"] for c in NEG_CASES]


@allure.feature("Authentication")
class TestLogin:
    """Test suite for user login functionality and security."""

    @allure.story("Happy Path")
    @allure.title("Standard user logs in successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_standard_user_login(self, cfg: MapObject, driver: WebDriver, login_page: LoginPage) -> None:
        """
        Verify that a standard user can log in with valid credentials
        and is redirected to the Inventory Page.
        """
        with Step(f"Attempt login for user: {cfg.credentials.username}"):
            login_page.login(cfg.credentials.username, cfg.credentials.password, is_sensitive=True)

        with Step("Verify redirection to the Inventory page"):
            inventory = InventoryPage(driver=driver)
            assert inventory.is_at(), "Login failed: The browser was not redirected to the Inventory Page."

    @allure.story("Negative Scenarios")
    @allure.title("Invalid login attempts validation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("case", NEG_CASES, ids=NEG_IDS)
    def test_login_failures(self, login_page: LoginPage, case: Dict[str, Any]) -> None:
        """
        Verify various negative login scenarios and ensure the correct error message is displayed.
        """
        allure.dynamic.title(f"Negative Test: {case['desc']}")

        with Step(f"Attempt login with username: '{case['user']}'"):
            login_page.login(case["user"], case["pass"])

        with Step("Verify the correct error message is displayed"):
            actual_error = login_page.get_error_message()
            assert login_page.is_at(), "Security Risk: Should remain on the Login page."
            assert actual_error == case["expected_error"], \
                f"Validation mismatch for scenario '{case['desc']}'. \n" \
                f"Expected: '{case['expected_error']}' \n" \
                f"Actual: '{actual_error}'"

    @allure.story("Security")
    @allure.title("Login credentials case sensitivity check")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "user_transform, pwd_transform, label",
        [
            pytest.param(lambda s: s.swapcase(), lambda s: s, "Swapped Username Case", id="swap_user"),
            pytest.param(lambda s: s, lambda s: s.swapcase(), "Swapped Password Case", id="swap_password")
        ]
    )
    def test_login_case_sensitivity(
            self, cfg: MapObject, driver: WebDriver, login_page: LoginPage,
            user_transform: Callable[[str], str], pwd_transform: Callable[[str], str], label: str
    ) -> None:
        """
        Verify that login fails if the casing of the username or password is incorrect.
        """
        allure.dynamic.title(f"Case Sensitivity Test: {label}")

        target_user = user_transform(cfg.credentials.username)
        target_pwd = pwd_transform(cfg.credentials.password)

        with Step(f"Attempt login with {label}"):
            login_page.login(target_user, target_pwd, is_sensitive=True)

        with Step("Verify login failed due to incorrect casing"):
            actual_error = login_page.get_error_message()
            assert login_page.is_at(), "Security Risk: Should remain on the Login page."
            assert "do not match" in actual_error, \
                f"Validation mismatch. Expected 'do not match' error, got: '{actual_error}'"

    @allure.story("Security")
    @allure.title("Prevent direct access to inventory without authentication")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_direct_access_prevention(self, driver: WebDriver) -> None:
        """
        Verify that an unauthenticated user cannot directly access the inventory page via URL.
        """
        inventory_page = InventoryPage(driver)

        with Step("Attempt to navigate directly to the inventory page"):
            inventory_page.load()

        with Step("Verify access is denied and user is redirected"):
            login_page = LoginPage(driver)
            assert login_page.is_at(), "Security Check Failed: User not on Login page."

        with Step("Verify relevant error message is displayed"):
            actual_error = login_page.get_error_message()
            expected_error = LOGIN_REQUIRED_INVENTORY_MSG
            assert actual_error == expected_error, \
                f"Expected error message containing '{expected_error}', but got '{actual_error}'"

    @allure.story("Session Management")
    @allure.title("Session persists across multiple tabs")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_multi_tab_login_persistence(self, driver: WebDriver, login_page: LoginPage) -> None:
        """
        Verify that once a user is logged in, opening a new tab and navigating
        to the app retains the logged-in state without requiring re-authentication.
        """
        with Step("Log in successfully in the first tab"):
            inventory_page = login_page.login_success("standard_user", "secret_sauce")

        with Step("Open a new tab and navigate to the inventory page directly"):
            driver.execute_script("window.open('about:blank', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            inventory_page.load()

        with Step("Verify the new tab is also logged in"):
            assert inventory_page.is_at(), "Session did not persist in the new tab."

    @allure.story("Security")
    @allure.title("Verify redirection to login page after session expiration")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_session_expired_redirection(self, driver: WebDriver, inventory_page: InventoryPage) -> None:
        """
        Simulate a session timeout by clearing browser cookies and verify the system
        denies access to protected pages.
        """
        with Step("Simulate session timeout by deleting all cookies"):
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear();")

        with Step("Attempt to interact with the page after 'timeout'"):
            driver.refresh()
            login_page = LoginPage(driver)

        with Step("Verify redirection to login page with appropriate error message"):
            assert login_page.is_at(), "User was not redirected back to the login page."
            actual_error = login_page.get_error_message()
            expected_error = LOGIN_REQUIRED_INVENTORY_MSG
            assert actual_error == expected_error, \
                f"Expected error message containing '{expected_error}', but got '{actual_error}'"


@allure.feature("Authentication")
class TestLogout:
    """Test suite for user logout functionality and session termination."""

    @allure.story("Happy Path")
    @allure.title("User logs out successfully from the main page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_success(self, driver: WebDriver, inventory_page: InventoryPage) -> None:
        """
        Verify that a logged-in user can successfully log out via the sidebar menu.
        """
        with Step("Execute logout flow via sidebar"):
            inventory_page.sidebar.open_menu().click_logout()
            login_page = LoginPage(driver=driver)

        with Step("Verify redirection to the Login page"):
            assert login_page.is_at(), "Logout Failed: Not redirected to the login page."

    @allure.story("Security")
    @allure.title("Session cookie is cleared upon logout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_clears_session_cookie(self, driver: WebDriver, inventory_page: InventoryPage) -> None:
        """
        Verify that the authentication cookie is completely removed from the browser.
        """
        auth_cookie_name = "session-username"

        with Step("Verify the authentication cookie exists before logging out"):
            assert driver.get_cookie(auth_cookie_name) is not None, \
                f"Expected cookie '{auth_cookie_name}' to be present."

        with Step("Perform logout flow"):
            inventory_page.sidebar.open_menu().click_logout()

        with Step("Verify the authentication cookie is deleted"):
            assert driver.get_cookie(auth_cookie_name) is None, \
                f"Security Risk: Cookie '{auth_cookie_name}' still exists after logout!"

    @allure.story("Security")
    @allure.title("Browser back button does not restore active session")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_security_back_button(self, driver: WebDriver, inventory_page: InventoryPage) -> None:
        """
        Verify that a user cannot navigate back to a protected page using the browser's
        back button after logging out.
        """
        with Step("Perform logout flow"):
            inventory_page.sidebar.open_menu().click_logout()
            login_page = LoginPage(driver=driver)

        with Step("Trigger browser back navigation"):
            driver.back()

        with Step("Verify the session remains terminated"):
            assert login_page.is_at(), "Security Check Failed: User not on Login page."

        with Step("Verify relevant error message is displayed"):
            actual_error = login_page.get_error_message()
            expected_error = LOGIN_REQUIRED_INVENTORY_MSG
            assert actual_error == expected_error, \
                f"Expected error message containing '{expected_error}', but got '{actual_error}'"

    @allure.story("Security")
    @allure.title("Multi-tab session sync upon logout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_multi_tab_sync(self, driver: WebDriver, inventory_page: InventoryPage) -> None:
        """
        Verify that logging out in one tab invalidates the session in all other open tabs.
        """
        with Step("Open a duplicate tab with the active session"):
            original_window = driver.current_window_handle
            driver.execute_script("window.open('about:blank', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            inventory_page.load()

        with Step("Perform logout in the secondary tab"):
            inventory_page.sidebar.open_menu().click_logout()
            login_page = LoginPage(driver=driver)
            assert login_page.is_at(), "Failed to logout in the secondary tab."

        with Step("Switch back to the primary tab and refresh"):
            driver.switch_to.window(original_window)
            driver.refresh()

        with Step("Verify the primary tab is also logged out"):
            assert login_page.is_at(), "Security Breach: Primary tab remained logged in."

        with Step("Verify relevant error message is displayed"):
            actual_error = login_page.get_error_message()
            expected_error = LOGIN_REQUIRED_INVENTORY_MSG
            assert actual_error == expected_error, \
                f"Expected error message containing '{expected_error}', but got '{actual_error}'"
