import zlib

from src.config import COMPRESSION_PREFIX


def compress_message(data: bytes) -> bytes:
    """
    Compresses data if it's convenient adding a compression tag
    at the start of the data.

    :param data: The data bytes to compress.
    :return: Compressed data bytes if it's convenient, otherwise
    the original data.
    """
    compressed = COMPRESSION_PREFIX.encode() + zlib.compress(data)
    if len(compressed) < len(data):
        return compressed

    return data


def decompress_message(data: bytes) -> bytes:
    """
    Decompresses data if it's compressed.

    :param data: Data bytes to decompress.
    :return: Decompressed data bytes.
    """
    if data.startswith(COMPRESSION_PREFIX.encode()):
        return zlib.decompress(data[len(COMPRESSION_PREFIX) :])

    return data
