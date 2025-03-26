import logging
import sys

from src.config import LOG_FORMAT, PROJECT_NAME


def __get_verbosity(verbosity: int) -> int:
    """
    Get logging level based on verbosity:
        - 0: NOT_SET,
        - 1: INFO,
        - >=2: DEBUG

    :param verbosity: Verbosity level
    :return: Logging level
    """
    if verbosity == 0:
        return logging.NOTSET
    elif verbosity == 1:
        return logging.INFO
    elif verbosity >= 2:
        return logging.DEBUG


def setup_logger(verbosity: int = 0):
    """
    Set up a logger with configurable verbosity levels.

    :param verbosity: Verbosity level
    :return: Configured logger
    """
    # Create a logger
    my_logger = logging.getLogger(PROJECT_NAME)
    my_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    my_logger.addHandler(console_handler)

    # Set logging level based on verbosity
    level = __get_verbosity(verbosity)
    my_logger.setLevel(level)

    return my_logger


logger = setup_logger()
