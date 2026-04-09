import logging
import os
from pathlib import Path

import yaml
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
AUTH_DIR = ROOT_DIR / "auth"


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

    try:
        config_obj.BASE_URL = getattr(config_obj.environments, config_obj.env)
    except AttributeError:
        raise ValueError(f"Environment '{config_obj.env}' is not defined in config.yaml")

    config_obj.credentials = MapObject({
        "username": os.getenv("STANDARD_USERNAME"),
        "password": os.getenv("STANDARD_PASSWORD")
    })

    env_headless = os.getenv("HEADLESS")
    if env_headless is not None:
        config_obj.driver.headless = env_headless.lower() == "true"

    return config_obj


global_config = load_config()