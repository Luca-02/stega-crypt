import logging
import sys

from src.config import LOG_FORMAT, LOGGING_LEVEL_LIST, PROJECT_NAME


def __get_verbosity_level(verbosity: int) -> int:
    """
    Get the logging level based on the input integer.

    :param verbosity: Verbosity level as an integer
    :return: Corresponding logging level
    """
    if verbosity < 0:
        verbosity = 0
    elif verbosity >= len(LOGGING_LEVEL_LIST):
        verbosity = len(LOGGING_LEVEL_LIST) - 1
    return LOGGING_LEVEL_LIST[verbosity]


def setup_logger(verbosity: int = 0):
    """
    Set up the global logger with configurable verbosity levels.

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

    level = __get_verbosity_level(verbosity)
    my_logger.setLevel(level)

    return my_logger


logger = setup_logger()
