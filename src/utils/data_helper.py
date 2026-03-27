import json
import logging
import os
from typing import Any, Dict, Union, List

from src.constants.constants import Paths

logger = logging.getLogger(__name__)


def load_json(file_name: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Load and parse a JSON file from the predefined data directory.

    Args:
        file_name (str): The name of the JSON file to load (e.g., 'test_users.json').

    Returns:
        Union[Dict[str, Any], List[Any]]: The parsed JSON data, typically returning
                                          a dictionary or a list depending on the file structure.

    Raises:
        FileNotFoundError: If the specified file does not exist in the data directory.
        json.JSONDecodeError: If the file exists but contains invalid JSON syntax.
        RuntimeError: If any other unexpected I/O error occurs during file reading.
    """
    file_path = os.path.join(Paths.DATA, file_name)

    if not os.path.exists(file_path):
        logger.error(f"Critical: Target JSON file '{file_path}' does not exist.")
        raise FileNotFoundError(f"Could not find the test data file at: {os.path.abspath(file_path)}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON. Invalid format in file: {file_path}")
        raise

    except Exception as e:
        logger.error(f"Unexpected I/O error while reading {file_path}: {e}")
        raise RuntimeError(f"Unexpected error loading JSON from {file_path}: {e}") from e