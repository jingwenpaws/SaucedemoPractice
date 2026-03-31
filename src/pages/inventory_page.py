from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from src.pages.base_page import BasePage
from src.pages.header_component import HeaderComponent
from src.pages.sidebar_page import SidebarPage
from src.utils.logger import Step


class InventoryPage(BasePage):
    """
    Page Object for the Inventory (Products) page.

    This page contains the product list and is typically accessed after a
    successful login.
    """
    URL_PATH = "/inventory.html"
    TITLE = (By.CLASS_NAME, "title")
    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.sidebar = SidebarPage(driver)
        self.header = HeaderComponent(self.driver)

    def is_at(self) -> bool:
        """
        Verify if the browser is currently on the Inventory page by checking
        the URL and the visibility of the page title.

        Returns:
            bool: True if both the URL matches and the title element is displayed.
        """
        url_matches = self.URL_PATH in self.driver.current_url
        title_visible = self.is_element_visible(self.TITLE)

        return url_matches and title_visible

    @Step("Add item '{item_name}' to the shopping cart")
    def add_item_to_cart(self, item_name: str) -> "InventoryPage":
        """
        Add a specific item to the shopping cart by its name.
        """
        pass
