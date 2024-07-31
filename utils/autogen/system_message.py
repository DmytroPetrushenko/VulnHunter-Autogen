import inspect
import os
import logging
import re

import constants
from constants import *
from typing import List
from errors.empty_file_error import EmptyFileError

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemMessage:
    def __init__(self):
        """
        Initialize the SystemMessage with default path and extension for message files.
        """
        self._path: str = 'agents_prompts'
        self._extension: str = '.txt'
        self._messages: dict = {}
        self._replacement_dict: dict = self._create_replacement_dict(constants)

    def load_messages(self, file_paths: List[str]) -> None:
        """
        Load messages from the specified file paths and store them in a dictionary.

        Args:
            file_paths (List[str]): List of file paths with version info.
        """

        for file_path in file_paths:
            base_name = os.path.basename(file_path)
            agent_name = base_name.split('#')[0]  # Remove version info

            full_file_path = os.path.join(self._path, f"{file_path}{self._extension}")

            message_str = None  # Initialize the variable before try block

            try:
                with open(full_file_path, 'r') as file_reader:
                    message_str = ' '.join(line.strip() for line in file_reader)
                    if not message_str:
                        raise EmptyFileError(f"The file {full_file_path} is empty")

                    message_str = self._replace_placeholders(
                        message_str)  # Replace placeholders in message_str with corresponding constants

            except FileNotFoundError:
                if agent_name not in [INITIALIZER, EXECUTOR]:
                    logger.error(f'{full_file_path} file is absent!')
            except EmptyFileError as e:
                logger.error(e)

            self._messages[agent_name] = message_str

    def get_system_message(self, key: str) -> str:
        """
        Retrieve the system message associated with the given key.

        Args:
            key (str): The key corresponding to the desired system message.

        Returns:
            str: The system message corresponding to the key, or an empty string if the key is not found.
        """
        return self._messages.get(key, '')

    def get_agents_names(self) -> List[str]:
        """
        Retrieve a list of agent names for which messages have been loaded.

        Returns:
            List[str]: List of agent names.
        """
        return list(self._messages.keys())

    def _replace_placeholders(self, text: str) -> str:
        """
        Replace placeholders in the text with corresponding values from the replacement dictionary.

        Args:
            text (str): The original text containing placeholders.

        Returns:
            str: The text with placeholders replaced.
        """

        def replacer(match):
            placeholder = match.group(1)  # Extract the text inside the braces
            return self._replacement_dict.get(placeholder,
                                        match.group(0))  # Replace with corresponding value from the dictionary

        return re.sub(TEXT_INSIDE_BRACES_PATTERN, replacer, text)

    @staticmethod
    def _create_replacement_dict(module, prefix=PREFIX_REPLACEMENT) -> dict:
        """
        Create a dictionary of constants from the given module that start with a specific prefix.

        Args:
            module: The module from which to extract constants.
            prefix (str): The prefix to filter constants.

        Returns:
            dict: A dictionary with constant names (without prefix) as keys and their values as values.
        """
        replacement_dict = {}
        for name, value in inspect.getmembers(module):
            if name.startswith(prefix) and isinstance(value, str):
                key = name[len(prefix):]  # Remove the prefix from the key
                replacement_dict[key] = value
        return replacement_dict
