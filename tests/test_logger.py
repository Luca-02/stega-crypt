import logging
import unittest

from src.config import LOG_FORMAT, LOGGING_LEVEL_LIST, PROJECT_NAME
from src.logger import setup_logger


class TestLogger(unittest.TestCase):
    def __assertion_logger(self, logger, level):
        self.assertEqual(logger.level, level)
        self.assertEqual(logger.name, PROJECT_NAME)
        self.assertTrue(
            any(
                isinstance(handler, logging.StreamHandler)
                for handler in logger.handlers
            )
        )
        self.assertTrue(
            any(
                handler.formatter._fmt == LOG_FORMAT
                for handler in logger.handlers
            )
        )

    def test_setup_logger(self):
        for level in range(len(LOGGING_LEVEL_LIST)):
            with self.subTest(level=level):
                logger = setup_logger(level)
                self.__assertion_logger(logger, LOGGING_LEVEL_LIST[level])

    def test_setup_logger_underflow_level(self):
        level = -1
        logger = setup_logger(level)
        self.__assertion_logger(logger, LOGGING_LEVEL_LIST[0])

    def test_setup_logger_overflow_level(self):
        level = len(LOGGING_LEVEL_LIST) + 1
        logger = setup_logger(level)
        self.__assertion_logger(logger, LOGGING_LEVEL_LIST[-1])
