import logging
import os
from datetime import datetime
from typing import Generator, Dict, Any

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from src.constants.constants import Paths
from src.pages.login_page import LoginPage
from src.pages.inventory_page import InventoryPage
from src.utils.browser_factory import _build_chrome_options, _build_firefox_options
from src.utils.config import Config

logger = logging.getLogger(__name__)
os.environ['WDM_LOG'] = '0'
logging.getLogger('WDM').setLevel(logging.WARNING)

# Dictionary to track logging handlers per test node ID
test_handlers: Dict[str, logging.FileHandler] = {}


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Add custom command-line options to pytest.
    """
    parser.addoption("--env", action="store", default="config", help="Environment config file name")


def pytest_configure(config: pytest.Config) -> None:
    """
    Dynamically configure settings before pytest execution begins.

    Creates a timestamped directory for the current test session to store logs and reports.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Paths.LOGS / f"session_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)

    # Store the session directory path in the pytest config object
    config._session_dir = session_dir


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    Execute setup logic before each test item.

    Creates a dedicated directory and log handler for the specific test case.
    """
    # Create a directory for the individual test case
    test_name = item.name.replace("[", "_").replace("]", "_")
    session_dir = item.config._session_dir
    test_case_dir = session_dir / test_name
    test_case_dir.mkdir(exist_ok=True)

    item._test_case_dir = test_case_dir

    # Configure the log file handler for the specific test
    test_log_path = test_case_dir / f"{test_name}.log"
    handler = logging.FileHandler(test_log_path, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)8s] %(message)s'))
    logging.getLogger().addHandler(handler)

    test_handlers[item.nodeid] = handler


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item: pytest.Item, nextitem: Any) -> None:
    """
    Execute teardown logic after each test item.

    Removes and closes the dedicated log handler for the test case to prevent resource leaks.
    """
    handler = test_handlers.pop(item.nodeid, None)
    if handler:
        handler.close()
        logging.getLogger().removeHandler(handler)


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
    logger.info("Initializing the browser session...")

    browser_name = cfg.driver.browser.lower()
    width = cfg.driver.window_size.width
    height = cfg.driver.window_size.height

    if browser_name == "chrome":
        options = _build_chrome_options(cfg)
        service = ChromeService(ChromeDriverManager().install())
        _driver = webdriver.Chrome(service=service, options=options)

    elif browser_name == "firefox":
        options = _build_firefox_options(cfg)
        service = FirefoxService(GeckoDriverManager().install())
        _driver = webdriver.Firefox(service=service, options=options)
        _driver.set_window_size(width, height)

    else:
        raise ValueError(f"Unsupported browser specified: {browser_name}")

    yield _driver

    logger.info("Terminating the browser session...")
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

    # Capture screenshot only when the test is executing ('call') and it fails
    if report.when == "call" and report.failed:
        error_message = str(report.longrepr)
        logging.error(f"Test case failed with the following error:\n{error_message}")
        try:
            # Retrieve the WebDriver instance from the test arguments
            driver = item.funcargs.get('driver')

            if driver:
                # Attach screenshot to Allure report
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name=f"screenshot_failed_case_{item.name}",
                    attachment_type=allure.attachment_type.PNG
                )

                # Optionally save the screenshot locally
                test_case_dir = getattr(item, "_test_case_dir", None)
                if test_case_dir:
                    file_path = test_case_dir / f"FAILED_{item.name}.png"
                    driver.save_screenshot(str(file_path))

        except Exception as e:
            # Replaced 'print' with 'logger.error' for proper log routing
            logger.error(f"Test hook failed to capture screenshot: {e}")