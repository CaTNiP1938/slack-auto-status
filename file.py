"""
    Contains I/O operation related functions used by the 'script.py' file
"""

import json
import os
import sys

from typing import Dict

CONFIG_FILE_PATH = 'config.json'


def read_configuration() -> Dict[str, any]:
    """
    Checks and reads in configration file

    Returns:
    Configuration in a dictionary form
    """

    # Construct absolute path by using this script's location
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, CONFIG_FILE_PATH)

    # Check if config file exists
    if not os.path.isfile(abs_file_path):
        print(
            "Configuration file is not present. " +
            "Please load the 'config.json' file into the directory!"
        )
        sys.exit(1)

    # Read config file into a dictionary
    return read_json_file(abs_file_path)


def read_json_file(filename: str) -> Dict[str, any]:
    """
    Reads json file into a dictionary

    Parameters:
    filename: str - The name of the file next to this one

    Returns:
    The file's content in JSON format
    """

    with open(filename) as f_in:
        return json.load(f_in)
