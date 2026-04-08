import logging
import os
import yaml
from typing import Dict, Any
from src.constants.constants import BASE_URLS, CONFIG_DIR
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class MapObject:
    """
    A utility class to convert a dictionary into an object.

    This allows configuration data to be accessed via dot notation
    (e.g., `config.driver.timeout` instead of `config['driver']['timeout']`).
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, MapObject(value))
            else:
                setattr(self, key, value)


def _get_base_url(env: str) -> str:
    if env in BASE_URLS:
        return BASE_URLS[env]
    if env.startswith(("http://", "https://")):
        return env
    raise ValueError(f"Invalid environment or URL: '{env}'.")


def load_config(config_name: str = "config") -> MapObject:
    """ Initialize and return the configuration object without handling Singleton logic.

        Loads data from the YAML file, assigns the base URL, and overrides
        specific settings (like credentials and headless mode) from the .env file.

        Args:
            config_name (str): The name of the YAML configuration file (without extension).

        Returns:
            MapObject: The fully constructed configuration object."""
    with open(CONFIG_DIR / f"{config_name}.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    config_obj = MapObject(data)

    config_obj.env = os.getenv("TEST_ENV", config_obj.env)
    config_obj.BASE_URL = _get_base_url(config_obj.env)

    config_obj.credentials = MapObject({
        "username": os.getenv("STANDARD_USERNAME"),
        "password": os.getenv("STANDARD_PASSWORD")
    })

    env_headless = os.getenv("HEADLESS")
    if env_headless is not None:
        config_obj.driver.headless = env_headless.lower() == "true"

    return config_obj


global_config = load_config()