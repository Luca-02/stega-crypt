import zlib


def compress_message(data) -> bytes:
    """
    Compresses data.

    :param data: The data to compress.
    :return: Compressed message as bytes.
    """
    return zlib.compress(data)


def decompress_message(data) -> bytes:
    """
    Decompresses data.

    :param data: Compressed data.
    :return: Decompressed message as bytes.
    """
    return zlib.decompress(data)
