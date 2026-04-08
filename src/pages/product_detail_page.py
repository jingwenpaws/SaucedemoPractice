from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from src.constants.constants import PageUrl
from src.pages.base_page import BasePage
from src.pages.header_component import HeaderComponent
from src.pages.sidebar_page import SidebarPage
from src.utils.logger import Step


class ProductDetailPageLocators:
    ITEM_NAME = (By.CSS_SELECTOR, "div[data-test='inventory-item-name']")
    ITEM_PRICES = (By.CSS_SELECTOR, "div[data-test='inventory-item-price']")
    ADD_CART = (By.CSS_SELECTOR, "button[data-test='add-to-cart']")
    REMOVE = (By.CSS_SELECTOR, "button[data-test='remove']")
    BACK_TO_PRODUCTS = (By.CSS_SELECTOR, "button[data-test='back-to-products']")


class ProductDetailPage(BasePage):
    """
    Page Object for the Inventory (Products) page.

    This page contains the product list and is typically accessed after a
    successful login.
    """
    URL_PATH = PageUrl.PRODUCT_DETAIL
    def __init__(self, driver: WebDriver, item_name: str) -> None:
        super().__init__(driver)
        self.item_name = item_name
        self.sidebar = SidebarPage(driver)
        self.header = HeaderComponent(self.driver)

    def is_at(self) -> bool:
        """
        Verify if the browser is currently on the Product Detail page by checking
        the URL and the visibility of the page title.

        Returns:
            bool: True if both the URL matches and the title element is displayed.
        """
        if not super().is_at():
            return False
        try:
            element = self.find_element(ProductDetailPageLocators.ITEM_NAME)
            item_name_matches = element.text == self.item_name
            return item_name_matches
        except TimeoutException:
            return False

    @Step("Back to the products page")
    def go_back_to_products_page(self):
        self.click(ProductDetailPageLocators.BACK_TO_PRODUCTS)