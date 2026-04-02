import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from src.constants.constants import PageUrls, DefaultItemAttributes
from src.pages.base_page import BasePage
from src.pages.header_component import HeaderComponent
from src.pages.sidebar_page import SidebarPage
from src.utils.logger import Step


class InventoryPageLocators:
    SORT_DROPDOWN = (By.CSS_SELECTOR, "select[data-test='product-sort-container']")
    ITEM_PRICES = (By.CSS_SELECTOR, "div[data-test='inventory-item-price']")
    ITEM_NAMES = (By.CSS_SELECTOR, "div[data-test='inventory-item-name']")
    ITEM_IMAGES = (By.CSS_SELECTOR, "img[data-test^='inventory-item-']")

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

    @staticmethod
    def item_name_link(item_name: str) -> tuple:
        return (By.XPATH, f"//div[@data-test='inventory-item-name' and text()='{item_name}']")

    @staticmethod
    def item_image_link(item_name: str) -> tuple:
        return (By.CSS_SELECTOR, f"img[alt='{item_name}']")


class InventoryPage(BasePage):
    """
    Page Object for the Inventory (Products) page.

    This page contains the product list and is typically accessed after a
    successful login.
    """
    URL_PATH = PageUrls.INVENTORY
    TITLE = (By.CLASS_NAME, "title")
    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.sidebar = SidebarPage(driver)
        self.header = HeaderComponent(self.driver)

    def is_at(self) -> bool:
        if not super().is_at():
            return False

        try:
            self.find_element(self.TITLE)
            return True
        except TimeoutException:
            return False

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
        self.click(locator)
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

    @Step("Click on item name '{item_name}' to view details")
    def click_item_name(self, item_name: str) -> None:
        locator = InventoryPageLocators.item_name_link(item_name)
        self.click(locator)

    @Step("Click on item image '{item_name}' to view details")
    def click_item_image(self, item_name: str) -> None:
        locator = InventoryPageLocators.item_image_link(item_name)
        self.click(locator)

    @Step("Check for any broken or incorrect (dog placeholder) images on the page")
    def get_broken_images(self) -> list[str]:
        """
        Verify all product images are fully loaded and are not replaced by placeholders.
        """
        images = self.find_elements(InventoryPageLocators.ITEM_IMAGES)
        broken_images = []

        for img in images:
            image_name = img.get_attribute("alt") or "Unknown Image"
            src = img.get_attribute("src")

            if src and DefaultItemAttributes.IMAGE_DOG_SLUG in src.lower():
                broken_images.append(f"{image_name} (Error: Replaced by the placeholder!)")
                continue

            is_loaded = self.driver.execute_script(
                "return typeof arguments[0].naturalWidth != 'undefined' && arguments[0].naturalWidth > 0;",
                img
            )

            if not is_loaded:
                broken_images.append(f"{image_name} (Error: Image broken or failed to load)")

        return broken_images
