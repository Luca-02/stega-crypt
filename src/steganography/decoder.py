import numpy as np

from config import DELIMITER_SUFFIX, COMPRESSION_PREFIX
from utility.compressor import decompress_message
from utility.file_handler import load_image


def decode_message(image_path: str) -> str:
    """
    Extracts the hidden message from an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the image containing the hidden message.

    :return: The hidden message extracted from the image.

    :raises FileNotFoundError: If the image file is not found.
    :raises UnidentifiedImageError: If the file is not a valid image.
    :raises ValueError: If no valid message was found.
    :raises Exception: For any other unexpected error.
    """
    image_data, _ = load_image(image_path)

    # Flatten the pixel arrays
    flat_data = image_data.flatten()

    # Extract Least-Significant-Bit
    lsb_data = flat_data & 1

    # Packs binary-valued array into 8-bits array.
    pack_data = np.packbits(lsb_data)

    # Read and convert integers to Unicode characters until hitting a non-printable character or the delimiter
    message_bytes = bytearray()
    for byte in pack_data:
        message_bytes.append(byte)
        if message_bytes.endswith(DELIMITER_SUFFIX.encode()):
            message_bytes = message_bytes[:-len(DELIMITER_SUFFIX)]
            break

    # If we found an empty message
    if not message_bytes:
        raise ValueError('No valid message found in the image.')

    if message_bytes.startswith(COMPRESSION_PREFIX.encode()):
        return decompress_message(message_bytes[len(COMPRESSION_PREFIX):]).decode()

    return message_bytes.decode()
