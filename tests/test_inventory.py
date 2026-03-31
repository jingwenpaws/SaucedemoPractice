import allure
import pytest

from src.constants.constants import InventoryTestData, InventoryItemsSortingValues
from src.pages.inventory_page import InventoryPage
from src.utils.logger import Step


@allure.feature("Inventory Page Actions")
class TestInventoryInteractions:
    """Test suite focusing purely on actions within the Inventory Page."""

    @allure.story("Cart Badge Updates")
    @allure.title("Adding an item updates the cart badge count")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_item_updates_cart_badge(self, inventory_page: InventoryPage) -> None:
        """Verify that adding a single item correctly updates the header cart badge to 1."""
        with Step("Add a single item to the cart"):
            inventory_page.add_item_to_cart(InventoryTestData.MAIN_PRODUCT)

        with Step("Verify the cart badge displays '1'"):
            assert inventory_page.header.get_cart_item_count() == 1, \
                "Cart badge count did not update to 1 after adding an item."

    @allure.story("Cart Badge Updates")
    @allure.title("Removing an item updates the cart badge count")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_remove_item_updates_badge(self, inventory_page: InventoryPage) -> None:
        """Verify that removing an item correctly decrements/removes the header cart badge."""
        with Step("Add an item to the cart"):
            inventory_page.add_item_to_cart(InventoryTestData.MAIN_PRODUCT)
            assert inventory_page.header.get_cart_item_count() == 1, \
                "Precondition failed: Cart badge is not 1."

        with Step("Remove the item from the cart"):
            inventory_page.remove_item_from_cart(InventoryTestData.MAIN_PRODUCT)

        with Step("Verify the cart badge disappears (count is 0)"):
            assert inventory_page.header.get_cart_item_count() == 0, \
                "Cart badge did not disappear after removing the item."

    @allure.story("Sorting")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "sorting_value, is_reverse, label",
        [
            pytest.param(InventoryItemsSortingValues.LOW_TO_HIGH, False, "Low to High", id="price_low_to_high"),
            pytest.param(InventoryItemsSortingValues.HIGH_TO_LOW, True, "High to Low", id="price_high_to_low")
        ]
    )
    def test_sort_by_price(self, inventory_page: InventoryPage, sorting_value: str, is_reverse: bool,
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
            pytest.param(InventoryItemsSortingValues.A_TO_Z, False, "A to Z", id="name_a_to_z"),
            pytest.param(InventoryItemsSortingValues.Z_TO_A, True, "Z to A", id="name_z_to_a")
        ]
    )
    def test_sort_by_name(self, inventory_page: InventoryPage, sorting_value: str, is_reverse: bool,
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