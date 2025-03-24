import logging
import sys

from src.config import LOG_FORMAT


def setup_logger(verbosity: int = 0):
    """
    Set up a logger with configurable verbosity levels.

    :param verbosity: Verbosity level (0: WARNING, 1: INFO, 2: DEBUG)
    :return: Configured logger
    """
    # Create a logger
    logger = logging.getLogger("stega-crypt")
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Set logging level based on verbosity
    if verbosity == 0:
        logger.setLevel(logging.WARNING)
    elif verbosity == 1:
        logger.setLevel(logging.INFO)
    elif verbosity >= 2:
        logger.setLevel(logging.DEBUG)

    return logger


my_logger = setup_logger()
