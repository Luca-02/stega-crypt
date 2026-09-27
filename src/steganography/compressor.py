import zlib

from src.config import COMPRESSION_PREFIX
from src.logger import logger


def compress_message(data: bytes) -> bytes:
    """Compress data when it is convenient, prepending a compression tag.

    Args:
        data: The data bytes to compress.

    Returns:
        The compression prefix followed by the compressed data if that is
        smaller than the input, otherwise the original data.
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
    """Decompress data if it starts with the compression prefix.

    Args:
        data: Data bytes to decompress.

    Returns:
        The decompressed data, or the input unchanged when the prefix is
        missing.
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
