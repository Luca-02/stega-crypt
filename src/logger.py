import logging
import sys

from src.config import LOG_FORMAT, PROJECT_NAME


def setup_logger(verbosity: int = 0):
    """
    Set up a logger with configurable verbosity levels.

    :param verbosity: Verbosity level
    (0: NOT_SET, 1: INFO, >=2: DEBUG)
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
    if verbosity == 0:
        my_logger.setLevel(logging.NOTSET)
    elif verbosity == 1:
        my_logger.setLevel(logging.INFO)
    elif verbosity >= 2:
        my_logger.setLevel(logging.DEBUG)

    return my_logger


logger = setup_logger()
