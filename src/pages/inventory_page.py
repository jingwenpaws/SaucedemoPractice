from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from src.pages.base_page import BasePage
from src.pages.header_component import HeaderComponent
from src.pages.sidebar_page import SidebarPage
from src.utils.logger import Step


class InventoryPageLocators:
    SORT_DROPDOWN = (By.CSS_SELECTOR, "select[data-test='product-sort-container']")
    ITEM_PRICES = (By.CSS_SELECTOR, "div[data-test='inventory-item-price']")
    ITEM_NAMES = (By.CSS_SELECTOR, "div[data-test='inventory-item-name']")

    @staticmethod
    def _to_slug(item_name: str) -> str:
        """Convert raw item name to slug format for data-test attributes."""
        return item_name.lower().replace(" ", "-")

    @classmethod
    def add_to_cart_button(cls, item_name: str) -> tuple:
        """Dynamic locator for the Add to Cart button based on the raw item name."""
        return (By.CSS_SELECTOR, f"button[data-test='add-to-cart-{cls._to_slug(item_name)}']")

    @classmethod
    def remove_button(cls, item_name: str) -> tuple:
        """Dynamic locator for the Remove button based on the raw item name."""
        return (By.CSS_SELECTOR, f"button[data-test='remove-{cls._to_slug(item_name)}']")


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
        Add a specific item to the shopping cart based on its visible name.

        Args:
            item_name: The exact text of the item name (e.g., "Sauce Labs Backpack").
        """
        locator = InventoryPageLocators.add_to_cart_button(item_name)
        self.click(locator)
        return self

    @Step("Remove item '{item_name}' from the shopping cart")
    def remove_item_from_cart(self, item_name):
        """
        Remove a specific item from the shopping cart based on its visible name.

        Args:
            item_name: The exact text of the item name (e.g., "Sauce Labs Backpack").
        """
        locator = InventoryPageLocators.remove_button(item_name)
        self.click(locator, force=True)
        return self

    @Step("Select {sort_value} to sort the inventory items")
    def select_sort_option_by_value(self, sort_value: str) -> None:
        """
        Sort the inventory items using the dropdown menu.
        Valid values: 'az' (A-Z), 'za' (Z-A), 'lohi' (Low to High), 'hilo' (High to Low).
        """
        locator = InventoryPageLocators.SORT_DROPDOWN

        self.select_dropdown_by_value(locator, sort_value)
        return self

    def get_all_item_prices(self) -> list[float]:
        """Get all item prices to a float list"""
        price_elements = self.find_elements(InventoryPageLocators.ITEM_PRICES)
        return [float(e.text.replace('$', '')) for e in price_elements]

    def get_all_item_names(self) -> list[str]:
        """Get all item names to a string list"""
        name_elements = self.find_elements(InventoryPageLocators.ITEM_NAMES)
        return [e.text for e in name_elements]
