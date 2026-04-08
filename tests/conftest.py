import logging
import os
from typing import Generator, Any

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from src.pages.login_page import LoginPage
from src.pages.inventory_page import InventoryPage
from src.utils.config import Config
from src.utils.browser_factory import _build_chrome_options

logger = logging.getLogger(__name__)
os.environ['WDM_LOG'] = '0'
logging.getLogger('WDM').setLevel(logging.WARNING)


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Add custom command-line options to pytest.
    """
    parser.addoption("--env", action="store", default="config", help="Environment config file name")


@pytest.fixture(scope="session")
def cfg(request: pytest.FixtureRequest) -> Any:
    """
    Initialize and provide the global configuration object based on the given environment.
    """
    env_name = request.config.getoption("--env")
    return Config.get(config_name=env_name)


@pytest.fixture(scope="function")
def driver(cfg: Any) -> Generator[webdriver.Remote, None, None]:
    """Initialize the Selenium WebDriver instance based on the configuration.

    Args:
        cfg: The configuration object containing browser settings.

    Yields:
        webdriver.Remote: The initialized Selenium WebDriver instance.
    """
    browser_name = cfg.driver.browser.lower()

    if browser_name == "chrome":
        options = _build_chrome_options(cfg)
        _driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    yield _driver
    _driver.quit()


@pytest.fixture(scope="function")
def login_page(driver: webdriver.Remote) -> Generator[LoginPage, None, None]:
    """
    Provide an instance of the LoginPage, fully loaded and verified.

    Args:
        driver (webdriver.Remote): The Selenium WebDriver instance.

    Yields:
        LoginPage: The initialized and verified LoginPage object.
    """
    yield LoginPage(driver).load().verify()

@pytest.fixture(scope="function")
def inventory_page(driver: webdriver.Remote, cfg: Any) -> Generator[InventoryPage, None, None]:
    """
    Provide an instance of the InventoryPage, fully loaded, verified.

    Args:
        driver (webdriver.Remote): The Selenium WebDriver instance.
        cfg: The configuration object containing browser settings.

    Yields:
        InventoryPage: The initialized, verified and login successfully InventoryPage object.
    """
    inventory_page = (LoginPage(driver).load().verify().login_success
                      (username=cfg.STANDARD_USERNAME, password=cfg.STANDARD_PASSWORD))
    inventory_page.verify()

    yield inventory_page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: Any) -> Generator[None, None, None]:
    """
    Hook to generate the test report.

    Captures a screenshot and attaches it to Allure if the test fails during execution.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get('driver')
        if driver:
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"FAILED_{item.name}",
                attachment_type=allure.attachment_type.PNG
            )
            browser_logs = "\n".join([str(log) for log in driver.get_log('browser')])
            allure.attach(browser_logs, name="Browser Logs", attachment_type=allure.attachment_type.TEXT)