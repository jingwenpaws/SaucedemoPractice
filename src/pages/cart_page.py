import logging

from selenium.webdriver.common.by import By
from src.pages.base_page import BasePage
from src.pages.header_component import HeaderComponent
from src.pages.sidebar_page import SidebarPage
from src.utils.logger import Step

logger = logging.getLogger(__name__)


class CartPageLocators:
    """
    Locators for the Cart Page elements.
    """
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "#checkout")
    INVENTORY_ITEM_NAME = (By.CSS_SELECTOR, ".inventory_item_name")


class CartPage(BasePage):
    """Page Object for the Shopping Cart page."""
    URL_PATH = "/cart.html"

    def __init__(self, driver):
        super().__init__(driver)
        self.header = HeaderComponent(driver)
        self.sidebar = SidebarPage(driver)

    def is_at(self) -> bool:
        """Verify if the browser is currently on the Cart page."""
        return self.URL_PATH in self.driver.current_url

    @Step("Verify if item '{item_name}' exists in the cart")
    def is_item_in_cart(self, item_name: str) -> bool:
        """
        Check if a specific item name is present in the cart list.

        Args:
            item_name: The exact text of the item name to search for.

        Returns:
            bool: True if the item is found, False otherwise.
        """
        elements = self.find_elements(CartPageLocators.INVENTORY_ITEM_NAME)
        item_names = [element.text for element in elements]
        logger.warning(item_names)
        return item_name in item_names

    @Step("Click the checkout button to proceed to the next step")
    def click_checkout(self) -> None:
        """
        Click the checkout button.
        (Note: Returns None. The test script will handle initializing the CheckoutPage.)
        """
        self.click(CartPageLocators.CHECKOUT_BUTTON)