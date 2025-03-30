import logging
import os

# Project info
PROJECT_NAME = "stega-crypt"
PROJECT_URL = "https://github.com/Luca-02/stega-crypt"
AUTHOR = "Luca Milanesi"

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
MODIFIED_IMAGE_SUFFIX = "-modified"
MESSAGE_NAME_SUFFIX = "-message"
ABOUT_PROJECT = (
    "\nThis tool combines steganography and cryptography to provide a "
    "secure way to hide sensitive messages within image files."
    "\nUsing the Least Significant Bit (LSB) technique, it embeds data "
    "in image pixels with minimal visual impact, while offering optional "
    "encryption and compression.\n"
    f"\nCreated by: {AUTHOR}"
    f"\nProject URL: {PROJECT_URL}\n"
)
