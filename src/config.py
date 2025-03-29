import logging
import os

# Project name
PROJECT_NAME = "stega-crypt"

# Project directories
DEFAULT_OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Message markers
COMPRESSION_PREFIX = "\x1f\x02"
DELIMITER_SUFFIX = "\x1f\x00"

# Cryptography settings
KEY_DERIVATION_HASH = "sha256"
KEY_DERIVATION_ITERATIONS = 100000
AES_KEY_LENGTH_BYTE = 32
SALT_SIZE_BYTE = 16
NONCE_SIZE_BYTE = 16
TAG_SIZE_BYTE = 16

# Steganography settings
MIN_PASSWORD_LENGTH = 4

# Logging configuration
LOG_FORMAT = "%(message)s"
LOGGING_LEVEL_LIST = (logging.NOTSET, logging.INFO, logging.DEBUG)

# String constants
ABOUT_PROJECT = f"""
{PROJECT_NAME} is a stenography tool designed for secure message hiding within images.
It utilizes also cryptographic techniques to ensure the confidentiality and integrity of the hidden messages.
"""
