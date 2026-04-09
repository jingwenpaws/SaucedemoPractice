import allure
import pytest

from src.pages.inventory_page import InventoryPage, SortOption
from src.pages.product_detail_page import ProductDetailPage
from src.utils.logger import Step


MAIN_PRODUCT_NAME = "Sauce Labs Backpack"


@allure.feature("Inventory Page Actions")
class TestInventoryInteractions:
    """Test suite focusing purely on actions within the Inventory Page."""

    @allure.story("Cart Badge Updates")
    @allure.title("Adding an item updates the cart badge count")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_item_updates_cart_badge(self, inventory_page: InventoryPage) -> None:
        """Verify that adding a single item correctly updates the header cart badge to 1."""
        with Step("Add a single item to the cart"):
            inventory_page.add_item_to_cart(MAIN_PRODUCT_NAME)

        with Step("Verify the cart badge displays '1'"):
            assert inventory_page.header.get_cart_item_count() == 1, \
                "Cart badge count did not update to 1 after adding an item."

    @allure.story("Cart Badge Updates")
    @allure.title("Removing an item updates the cart badge count")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_remove_item_updates_badge(self, inventory_page: InventoryPage) -> None:
        """Verify that removing an item correctly decrements/removes the header cart badge."""
        with Step("Add an item to the cart"):
            inventory_page.add_item_to_cart(MAIN_PRODUCT_NAME)
            assert inventory_page.header.get_cart_item_count() == 1, \
                "Precondition failed: Cart badge is not 1."

        with Step("Remove the item from the cart"):
            inventory_page.remove_item_from_cart(MAIN_PRODUCT_NAME)

        with Step("Verify the cart badge disappears (count is 0)"):
            assert inventory_page.header.get_cart_item_count() == 0, \
                "Cart badge did not disappear after removing the item."

    @allure.story("Sorting")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "sorting_value, is_reverse, label",
        [
            pytest.param(SortOption.LOW_TO_HIGH, False, "Low to High", id="price_low_to_high"),
            pytest.param(SortOption.HIGH_TO_LOW, True, "High to Low", id="price_high_to_low")
        ]
    )
    def test_sort_by_price(self, inventory_page: InventoryPage, sorting_value: SortOption, is_reverse: bool,
                           label: str) -> None:
        """Verify that the inventory items can be correctly sorted by price."""
        allure.dynamic.title(f"Verify items can be sorted by price ({label})")

        with Step(f"Select sorting: {label}"):
            inventory_page.select_sort_option_by_value(sorting_value)

        with Step("Verify price sorting logic"):
            actual_prices = inventory_page.get_all_item_prices()
            expected_prices = sorted(actual_prices, reverse=is_reverse)

            assert actual_prices == expected_prices, \
                f"Price sorting failed for '{label}'. Expected: {expected_prices}, Actual: {actual_prices}"

    @allure.story("Sorting")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "sorting_value, is_reverse, label",
        [
            pytest.param(SortOption.A_TO_Z, False, "A to Z", id="name_a_to_z"),
            pytest.param(SortOption.Z_TO_A, True, "Z to A", id="name_z_to_a")
        ]
    )
    def test_sort_by_name(self, inventory_page: InventoryPage, sorting_value: SortOption, is_reverse: bool,
                          label: str) -> None:
        """Verify that the inventory items can be correctly sorted by name."""
        allure.dynamic.title(f"Verify items can be sorted by name ({label})")

        with Step(f"Select sorting: {label}"):
            inventory_page.select_sort_option_by_value(sorting_value)

        with Step("Verify name sorting logic"):
            actual_names = inventory_page.get_all_item_names()
            expected_names = sorted(actual_names, reverse=is_reverse)

            assert actual_names == expected_names, \
                f"Name sorting failed for '{label}'. Expected: {expected_names}, Actual: {actual_names}"

    @pytest.mark.parametrize(
        "click_logic, label",
        [
            pytest.param(lambda page, item: page.click_item_name(item), 'name'),
            pytest.param(lambda page, item: page.click_item_image(item), 'image')
    ], ids=["name_click", "image_click"])
    def test_navigate_to_product_detail(self, driver, inventory_page: InventoryPage, click_logic, label) -> None:
        """Verify that clicking a product name or image opens its detail page."""
        allure.dynamic.title(f"Clicking an item {label} navigates to the Product Detail Page")
        target_item = MAIN_PRODUCT_NAME
        with Step(f"Click on the product {label}: '{target_item}'"):
            click_logic(inventory_page, target_item)

        with Step("Verify navigation to the Product Detail Page"):
            product_detail_page = ProductDetailPage(driver, target_item)
            assert product_detail_page.is_at(), \
                f"Failed to navigate to the {target_item} product detail page."

    @allure.story("Navigation")
    @allure.title("Dynamic Exhaustive Test: Verify all visible items can navigate to PDP")
    def test_all_products_navigable(self, driver, inventory_page: InventoryPage) -> None:
        """Dynamically fetch all items on the page and verify their navigation."""

        with Step("Fetch all available product names from the current page"):
            all_item_names = inventory_page.get_all_item_names()

        with Step("Iterate through each product and verify navigation"):
            failed_items = []
            for item_name in all_item_names:
                try:
                    inventory_page.click_item_name(item_name)

                    product_detail_page = ProductDetailPage(driver, item_name)
                    assert product_detail_page.is_at()

                    product_detail_page.go_back_to_products_page()
                    assert inventory_page.is_at(), "Failed to wait for the inventory page to reload after going back."

                except Exception as e:
                    failed_items.append(f"'{item_name}' failed: {str(e)}")
                    inventory_page.load().verify()

            if failed_items:
                formatted_errors = "\n- ".join(failed_items)
                error_message = f"The following {len(failed_items)} items failed navigation:\n- {formatted_errors}"

                pytest.fail(error_message)

    @allure.story("UI Integrity")
    @allure.title("Verify all product images load successfully without broken links")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_product_images_loaded(self, inventory_page: InventoryPage) -> None:
        """Verify that no broken images are displayed on the inventory page."""

        with Step("Scan all product images for rendering failures"):
            broken_images = inventory_page.get_broken_images()

        with Step("Verify the broken images list is empty"):
            if broken_images:
                formatted_errors = "\n- ".join(broken_images)
                error_message = f"Found {len(broken_images)} broken images on the page:\n- {formatted_errors}"

                pytest.fail(error_message)