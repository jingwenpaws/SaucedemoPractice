"""
A. 負面測試 (Negative Testing)

正確帳號 + 錯誤密碼

錯誤帳號 + 正確密碼

帳號空白 + 點擊登入 (驗證錯誤提示字眼)

密碼空白 + 點擊登入

被鎖定的帳號 (SauceDemo 剛好有提供 locked_out_user)

B. 邊界與安全性測試 (Security/Edge Cases)

繞過登入 (Direct Access)：在「未登入」的狀態下，直接用 driver.get("https://.../inventory.html")。預期結果：系統應該要擋下你，並自動跳轉回登入頁，或是顯示「請先登入」的錯誤訊息。（這條必測！）

大小寫敏感度：帳號或密碼輸入大寫，是否會被拒絕？

4. 登出還可以測什麼？ (Logout Test Ideas)
登出通常與「Session (工作階段)」的清除有關：

跨頁面登出：在商品列表頁 (Inventory) 登出會成功，那如果在購物車頁 (Cart) 打開側邊欄登出，會成功嗎？

多分頁測試 (Multi-tab)：打開兩個分頁都處於登入狀態，在分頁 A 點擊登出，然後切換到分頁 B 點擊重新整理。預期結果：分頁 B 也應該變成登出狀態。

Cookie 清除驗證：登出後，透過 driver.get_cookies() 檢查代表身分驗證的 Cookie 是否已經被刪除。
"""
import pytest
import allure
from typing import Dict, Any

from selenium.webdriver.remote.webdriver import WebDriver
from src.utils.data_helper import load_json
from src.pages.inventory_page import InventoryPage
from src.pages.login_page import LoginPage
from src.utils.config import Config
from tests.conftest import login_page
from src.utils.logger import Step

# Load test data globally for parametrization
_LOGIN_DATA = load_json("login_data.json")
NEG_CASES = _LOGIN_DATA["negative_test_users"]
NEG_IDS = [c["id"] for c in NEG_CASES]


@allure.feature("Login Functionality")
class TestLogin:

    @allure.story("Valid Login")
    @allure.title("Standard User Login Successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_standard_user_login(self, cfg: Config, driver: WebDriver, login_page: LoginPage) -> None:
        """
        Verify that a standard user can successfully log in with valid credentials
        and is successfully redirected to the Inventory Page.

        Args:
            cfg (Config): The configuration object containing system environment variables.
            driver (WebDriver): The Selenium WebDriver instance.
            login_page (LoginPage): The initialized Login Page object.
        """
        with Step(f"Attempting login for standard user: {cfg.STANDARD_USERNAME}"):
            login_page.login(cfg.STANDARD_USERNAME, cfg.STANDARD_PASSWORD)

        with Step("Verify successful redirection to the Inventory page"):
            # Using the driver fixture directly to initialize the next page
            inventory = InventoryPage(driver=driver)
            assert inventory.is_at(), "Login failed: The browser was not redirected to the Inventory Page."

    @allure.story("Negative Login Scenarios")
    @allure.title("Invalid Login Attempts")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("case", NEG_CASES, ids=NEG_IDS)
    def test_login_failures(self, login_page: LoginPage, case: Dict[str, Any]) -> None:
        """
        Verify various negative login scenarios (e.g., incorrect password,
        non-existent account) and ensure the correct error message is displayed.

        Args:
            login_page (LoginPage): The initialized Login Page object.
            case (Dict[str, Any]): A dictionary containing test data for a specific
                                   negative scenario (keys: user, pass, expected_error, desc).
        """
        allure.dynamic.title(f"Negative Test: {case['desc']}")

        with Step(f"Attempting login with username: '{case['user']}'"):
            login_page.login(case["user"], case["pass"])

        with Step("Verify the correct error message is displayed"):
            actual_error = login_page.get_error_message()

        assert actual_error == case["expected_error"], \
            f"Validation mismatch for scenario '{case['desc']}'. \n" \
            f"Expected: '{case['expected_error']}' \n" \
            f"Actual: '{actual_error}'"

@allure.feature("Logout Functionality")
class TestLogout:
    @allure.story("Logout Flow")
    @allure.title("A User Logout Successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_success(self, driver: WebDriver, inventory_page: InventoryPage):
        with Step("Logout the page"):
            inventory_page.sidebar.open_menu().click_logout()
            login_page = LoginPage(driver=driver)

        assert login_page.is_at()

    @allure.story("Security")
    @allure.title("A User Logout Successfully cannot go back to recover the login status")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_security_back_button(self, driver: WebDriver, inventory_page: InventoryPage):
        with Step("Logout the page"):
            inventory_page.sidebar.open_menu().click_logout()
            login_page = LoginPage(driver=driver).verify()
        with Step("Go back to the previous page"):
            driver.back()

        assert inventory_page.is_at() is False
        assert login_page.is_at()
