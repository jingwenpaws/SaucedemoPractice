from pathlib import Path


# page urls
class PageUrls:
    LOGIN = "/"
    INVENTORY = "/inventory.html"
    PRODUCT_DETAIL = "/inventory-item.html"
    CART = "/cart.html"
    CHECKOUT_INFO = "/checkout-step-one.html"


# paths
class Paths:
    ROOT = Path(__file__).resolve().parent.parent.parent
    DATA = ROOT / "data"
    LOGS = ROOT / "logs"
    CONFIG = ROOT / "config"

class InventoryTestData:
    MAIN_PRODUCT = "Sauce Labs Backpack"


class InventoryItemsSortingValues:
    LOW_TO_HIGH = "lohi"
    HIGH_TO_LOW = "hilo"
    A_TO_Z = "az"
    Z_TO_A = "za"


class DefaultItemAttributes:
    IMAGE_DOG_SLUG = "sl-404"


# base url
BASE_URLS = {
    "prod": "https://www.saucedemo.com",
    # The options below are to show the flexibilities to switch the env
    # However, actually we don't have permission to access these environments of saucedemo.com
    # That's why all environments are the same as production
    "qa": "https://www.saucedemo.com",
    "staging": "https://www.saucedemo.com"
}