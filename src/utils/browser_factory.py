import logging
from typing import Any
from selenium import webdriver

logger = logging.getLogger(__name__)


def _build_chrome_options(cfg: Any) -> webdriver.ChromeOptions:
    """Builds and returns the ChromeOptions based on the configuration."""
    options = webdriver.ChromeOptions()

    arguments = [
        "--incognito",
        "--disable-search-engine-choice-screen",
        "--disable-blink-features=AutomationControlled",
        f"--window-size={cfg.driver.window_size.width},{cfg.driver.window_size.height}"
    ]

    if cfg.driver.headless:
        arguments.extend(["--headless=new", "--no-sandbox", "--disable-dev-shm-usage"])

    for arg in arguments:
        options.add_argument(arg)

    # 排除自動化提示即可
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return options

def _build_firefox_options(cfg: Any) -> webdriver.FirefoxOptions:
    """Builds and returns the FirefoxOptions based on the configuration."""
    options = webdriver.FirefoxOptions()
    if cfg.driver.headless:
        options.add_argument("-headless")
    return options