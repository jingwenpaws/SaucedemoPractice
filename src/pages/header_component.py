from selenium.webdriver.common.by import By
from typing import TYPE_CHECKING
from src.pages.base_ui import BaseUI
from src.utils.logger import Step

if TYPE_CHECKING:
    from src.pages.cart_page import CartPage


class HeaderLocators:
    """
    Locators for the Top Navigation Bar (Header) elements.
    """
    CART_ICON = (By.CSS_SELECTOR, ".shopping_cart_link")
    CART_BADGE = (By.CSS_SELECTOR, ".shopping_cart_badge")
    APP_LOGO = (By.CSS_SELECTOR, ".app_logo")


class HeaderComponent(BaseUI):
    """
    Component object for the Top Navigation Bar.

    This component is shared across multiple pages and handles overarching
    navigation features like accessing the shopping cart.
    """

    @Step("Retrieve the current item count from the shopping cart badge")
    def get_cart_item_count(self) -> int:
        """
        Get the number of items currently displayed on the cart badge.

        Returns:
            int: The number of items in the cart. Returns 0 if the badge is not visible.
        """
        if self.is_element_visible(HeaderLocators.CART_BADGE, timeout=1):
            badge_text = self.find_element(HeaderLocators.CART_BADGE).text
            return int(badge_text)

        return 0

    @Step("Click the shopping cart icon")
    def click_cart(self) -> "CartPage":
        """
        Click the shopping cart icon to navigate to the Cart Page.

        Returns:
            CartPage: The page object for the Cart Page.
        """
        self.click(HeaderLocators.CART_ICON)
        from src.pages.cart_page import CartPage
        return CartPage(self.driver)
