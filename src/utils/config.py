import logging
import os
import threading
import yaml
from typing import Optional, Dict, Any

from src.constants.constants import Paths, BASE_URLS
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
        """
        Recursively initialize the MapObject with dictionary data.

        Args:
            data (Dict[str, Any]): The dictionary containing configuration data.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, MapObject(value))
            else:
                setattr(self, key, value)


class Config:
    """
    Singleton Configuration Manager.

    Responsible for loading YAML configuration files, parsing environment variables,
    and providing a globally accessible, thread-safe configuration object.
    """
    _instance: Optional[MapObject] = None
    _lock = threading.Lock()

    @classmethod
    def _get_base_url(cls, env: str) -> str:
        """
        Private method to resolve the base URL based on the environment string.

        Args:
            env (str): The environment name (e.g., 'qa', 'prod') or a direct URL.

        Returns:
            str: The resolved base URL.

        Raises:
            ValueError: If the environment string is neither a predefined environment
                        nor a valid URL.
        """
        if env in BASE_URLS:
            return BASE_URLS[env]

        if env.startswith(("http://", "https://")):
            logger.warning(f"Environment '{env}' not found in constants. Using it as a direct URL.")
            return env

        available_envs = list(BASE_URLS.keys())
        raise ValueError(
            f"Invalid environment or URL: '{env}'. "
            f"Please use one of {available_envs} or provide a full URL starting with http/https."
        )

    @classmethod
    def _initialize_config(cls, config_name: str) -> MapObject:
        """
        Initialize and return the configuration object without handling Singleton logic.

        Loads data from the YAML file, assigns the base URL, and overrides
        specific settings (like credentials and headless mode) from the .env file.

        Args:
            config_name (str): The name of the YAML configuration file (without extension).

        Returns:
            MapObject: The fully constructed configuration object.
        """
        logger.info(f"Initializing configuration for the first time. Loading: {config_name}.yaml")

        with open(Paths.CONFIG / f"{config_name}.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        config_obj = MapObject(data)
        override_env = os.getenv("TEST_ENV")
        if override_env:
            logger.info(f"Overriding YAML environment with OS TEST_ENV: '{override_env}'")
            config_obj.env = override_env

        config_obj.BASE_URL = cls._get_base_url(config_obj.env)

        config_obj.STANDARD_USERNAME = os.getenv("STANDARD_USERNAME")
        config_obj.STANDARD_PASSWORD = os.getenv("STANDARD_PASSWORD")

        env_headless = os.getenv("HEADLESS")
        if env_headless is not None:
            config_obj.driver.headless = env_headless.lower() == "true"

        return config_obj

    @classmethod
    def get(cls, config_name: str = "config") -> MapObject:
        """
        Retrieve the Singleton instance of the configuration object.

        Ensures thread-safe initialization on the first call.

        Args:
            config_name (str): The name of the configuration file to load. Defaults to "config".

        Returns:
            MapObject: The Singleton configuration instance.
        """
        if cls._instance is not None:
            return cls._instance

        # Use a lock to ensure thread safety during initialization
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls._initialize_config(config_name)

        return cls._instance
