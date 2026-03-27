from pathlib import Path


# paths
class Paths:
    ROOT = Path(__file__).resolve().parent.parent.parent
    DATA = ROOT / "data"
    LOGS = ROOT / "logs"
    CONFIG = ROOT / "config"


# base url
BASE_URLS = {
    "prod": "https://www.saucedemo.com",
    "qa": "https://xxx.qa.com"
}