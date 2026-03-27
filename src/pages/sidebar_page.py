from selenium.webdriver.common.by import By
from src.pages.base_ui import BaseUI
from selenium.webdriver.support import expected_conditions as EC


class SidebarPageLocators:
    """
    Locators for the Sidebar elements.
    """
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    CLOSE_BUTTON = (By.ID, "react-burger-cross-btn")
    MENU_WRAP = (By.CLASS_NAME, "bm-menu-wrap")


class SidebarPage(BaseUI):
    """
    Component object for the Sidebar (Hamburger menu).

    This component handles actions within the slide-out sidebar menu,
    such as navigating to different app sections, logging out, or resetting the app state.
    """

    def open_menu(self) -> "SidebarPage":
        """
        Open the sidebar menu and wait for the slide-out CSS animation to complete.

        Returns:
            SidebarPage: The current instance for method chaining.
        """
        self.click(SidebarPageLocators.MENU_BUTTON)
        self.wait.until(
            EC.text_to_be_present_in_element_attribute(
                SidebarPageLocators.MENU_WRAP, "aria-hidden", "false"
            )
        )
        return self

    def click_logout(self) -> None:
        """
        Click the logout link within the sidebar.

        Note:
            Uses a forced JavaScript click to bypass intermittent click interception
            issues caused by the sidebar's 3D transform animation in Headless Chrome.
        """
        self.click(SidebarPageLocators.LOGOUT_LINK, force=True)

    def close_menu(self) -> "SidebarPage":
        """
        Close the sidebar menu.

        Returns:
            SidebarPage: The current instance for method chaining.
        """
        self.click(SidebarPageLocators.CLOSE_BUTTON)
        return self