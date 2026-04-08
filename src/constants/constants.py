"""Global constants and enumerations for the automation framework.

This module defines file paths, page URLs, sorting options, and default
test data used across the testing suite.
"""

from enum import Enum
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
CONFIG_DIR = ROOT_DIR / "config"


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
class PageUrl(str, Enum):
    """Enumeration of application page endpoints."""
    LOGIN = "/"
    INVENTORY = "/inventory.html"
    PRODUCT_DETAIL = "/inventory-item.html"
    CART = "/cart.html"
    CHECKOUT_INFO = "/checkout-step-one.html"


class SortOption(str, Enum):
    """Enumeration of inventory sorting values."""
    LOW_TO_HIGH = "lohi"
    HIGH_TO_LOW = "hilo"
    A_TO_Z = "az"
    Z_TO_A = "za"


# ---------------------------------------------------------------------------
# Test Data & Attributes
# ---------------------------------------------------------------------------
MAIN_PRODUCT_NAME = "Sauce Labs Backpack"
IMAGE_DOG_SLUG = "sl-404"


# ---------------------------------------------------------------------------
# Error Messages
# ---------------------------------------------------------------------------
ACCESS_DENIED_TEMPLATE = (
    "Epic sadface: You can only access '{path}' when you are logged in."
)

LOGIN_REQUIRED_INVENTORY_MSG = ACCESS_DENIED_TEMPLATE.format(
    path=PageUrl.INVENTORY.value
)
LOGIN_REQUIRED_ITEM_MSG = ACCESS_DENIED_TEMPLATE.format(
    path=PageUrl.PRODUCT_DETAIL.value
)


# ---------------------------------------------------------------------------
# Environments
# ---------------------------------------------------------------------------
BASE_URLS = {
    "prod": "https://www.saucedemo.com",
    "qa": "https://www.saucedemo.com",
    "staging": "https://www.saucedemo.com",
}