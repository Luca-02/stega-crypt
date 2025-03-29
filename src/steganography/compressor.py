import zlib

from src.config import COMPRESSION_PREFIX
from src.logger import logger


def compress_message(data: bytes) -> bytes:
    """
    Compresses data if it's convenient adding a compression tag
    at the start of the data.

    :param data: The data bytes to compress.
    :return: Compressed data bytes if it's convenient, otherwise
    the original data.
    """
    logger.info(
        f"Attempting to compress data (original size: {len(data)} bytes)"
    )

    compressed = COMPRESSION_PREFIX.encode() + zlib.compress(data)

    if len(compressed) < len(data):
        logger.info(f"Compression successful: size={len(compressed)} bytes")
        return compressed

    logger.info("Compression not beneficial, using original data")
    return data


def decompress_message(data: bytes) -> bytes:
    """
    Decompresses data if it's compressed.

    :param data: Data bytes to decompress.
    :return: Decompressed data bytes.
    """
    logger.info(
        f"Checking if data needs decompression (size: {len(data)} bytes)"
    )

    if data.startswith(COMPRESSION_PREFIX.encode()):
        logger.debug("Compression prefix found. Decompressing data")
        decompressed = zlib.decompress(data[len(COMPRESSION_PREFIX) :])
        logger.debug(f"Decompressed data size: {len(decompressed)} bytes")
        return decompressed

    logger.debug("No compression detected")
    return data
