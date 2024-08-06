# perf_logger.py

import logging
from datetime import datetime

# Set up the logger
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


class TaskTimeLogger:

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.start_time_point = datetime.now()
        self.duration_logging_enabled = False
        self.init_logger()

    def init_logger(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def enable_logging(self):
        self.duration_logging_enabled = True

    def disable_logging(self):
        self.duration_logging_enabled = False

    def log_start(self):
        """
        Logs the start time with the module name.
        """
        if self.duration_logging_enabled:
            self.logger.info(f'module: {self.module_name} - Start: {self.start_time_point.strftime("%H:%M:%S")}')

    def log_duration(self, message: str):
        """
        Logs the duration of a process with the module name and message.

        Args:
            message (str): The message to log.
        """
        if self.duration_logging_enabled:
            duration = (datetime.now() - self.start_time_point).total_seconds()
            self.logger.info(f'module: {self.module_name} - {message} duration: {duration:.6f} seconds')

    def info(self, message: str):
        """
        Logs an info message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(f'module: {self.module_name} - {message}')

    def warning(self, message: str):
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        self.logger.warning(f'module: {self.module_name} - {message}')

    def error(self, message: str):
        """
        Logs an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(f'module: {self.module_name} - {message}')

    def get_duration(self):
        return (datetime.now() - self.start_time_point).total_seconds()
