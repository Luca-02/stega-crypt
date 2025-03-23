import os

# Project directories
DEFAULT_OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Message markers
COMPRESSION_PREFIX = "\x01CMP"
DELIMITER_SUFFIX = "\x00D\x00"

# Cryptography settings
KEY_DERIVATION_ITERATIONS = 100000
AES_KEY_LENGTH_BYTE = 32
SALT_SIZE_BYTE = 16
NONCE_SIZE_BYTE = 16
TAG_SIZE_BYTE = 16

# Steganography settings
MIN_PASSWORD_LENGTH = 4
