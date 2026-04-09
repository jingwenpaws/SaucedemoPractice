"""Utility module for handling data file operations.

This module provides helper functions to read and parse external data files
(like JSON) used for data-driven testing.
"""

import json
import logging
from typing import Any, Dict, List, Union

from src.utils.config import DATA_DIR

logger = logging.getLogger(__name__)


def load_json(file_name: str) -> Union[Dict[str, Any], List[Any]]:
    """Loads and parses a JSON file from the predefined data directory.

    Args:
        file_name: The name of the JSON file to load (e.g., 'test_users.json').

    Returns:
        Union[Dict[str, Any], List[Any]]: The parsed JSON data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON syntax.
        RuntimeError: If any other unexpected I/O error occurs.
    """
    file_path = DATA_DIR / file_name

    if not file_path.exists():
        logger.error(f"Critical: Target JSON file '{file_path}' does not exist.")
        raise FileNotFoundError(f"Could not find the test data file at: {file_path.resolve()}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON. Invalid format in file: {file_path}")
        raise

    except Exception as e:
        logger.error(f"Unexpected I/O error while reading {file_path}: {e}")
        raise RuntimeError(f"Unexpected error loading JSON from {file_path}: {e}") from e