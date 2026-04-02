from selenium.webdriver.common.by import By

from src.constants.constants import PageUrls
from src.pages.base_page import BasePage
from src.pages.header_component import HeaderComponent
from src.pages.sidebar_page import SidebarPage
from src.utils.logger import Step



class CartPageLocators:
    """
    Locators for the Cart Page elements.
    """
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "#checkout")
    INVENTORY_ITEM_NAME = (By.CSS_SELECTOR, ".inventory_item_name")


class CartPage(BasePage):
    """Page Object for the Shopping Cart page."""

    URL_PATH = PageUrls.CART
    def __init__(self, driver):
        super().__init__(driver)
        self.header = HeaderComponent(driver)
        self.sidebar = SidebarPage(driver)

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
        self.logger.warning(item_names)
        return item_name in item_names

    @Step("Click the checkout button to proceed to the next step")
    def click_checkout(self) -> None:
        """
        Click the checkout button.
        (Note: Returns None. The test script will handle initializing the CheckoutPage.)
        """
        self.click(CartPageLocators.CHECKOUT_BUTTON)