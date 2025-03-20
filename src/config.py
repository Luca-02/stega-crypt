import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(PROJECT_ROOT, '.output')

COMPRESSION_PREFIX = '\x01CMP'

DELIMITER_SUFFIX = '\x00D\x00'
