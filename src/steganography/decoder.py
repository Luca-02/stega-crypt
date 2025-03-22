from typing import Optional

import numpy as np

from src.steganography.file_handler import load_image

from ..config import COMPRESSION_PREFIX, DELIMITER_SUFFIX
from ..cryptography.decrypt import decrypt_message
from .compressor import decompress_message


def __extract_lsb_data(image_data: np.ndarray) -> np.ndarray:
    """
    Extract the least significant bits from the image data.

    :param image_data: NumPy array of image data.
    :return: NumPy array of extracted LSB bits.
    """
    # Flatten the pixel arrays
    flat_data = image_data.flatten()

    # Extract just the least significant bit from each byte
    lsb_bits = flat_data & 1

    return lsb_bits


def __process_extracted_data(lsb_data: np.ndarray) -> bytearray:
    """
    Process extracted data retrieving the hidden data, handling compression if present.

    :param lsb_data: Raw extracted data from the image LSB.
    :return: Processed data, decompressed if needed.
    """

    # Packs binary-valued array into 8-bits array.
    pack_data = np.packbits(lsb_data)

    # Read and convert integers to Unicode characters until
    # hitting a non-printable character or the delimiter
    delimiter_suffix_encoded = DELIMITER_SUFFIX.encode()
    message_bytes = bytearray()
    for byte in pack_data:
        message_bytes.append(byte)

        if message_bytes.endswith(delimiter_suffix_encoded):
            message_bytes = message_bytes[: -len(DELIMITER_SUFFIX)]
            break

    # Decompress if its compressed
    compression_prefix_encoded = COMPRESSION_PREFIX.encode()
    if message_bytes.startswith(compression_prefix_encoded):
        message_bytes = decompress_message(message_bytes[len(COMPRESSION_PREFIX) :])

    return message_bytes


def decode_message(image_path: str, password: Optional[str] = None) -> str:
    """
    Extracts the hidden message from an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the image containing the hidden message.
    :param password: The password to decrypt the hidden message.
    If not specified the message will not be decrypted.
    :return: The hidden message extracted from the image.
    :raises ImageFileNotFoundError: If the image file is not found.
    :raises UnidentifiedImageError: If the file is not a valid image.
    :raises NoMessageFoundError: If no valid message was found.
    :raises Exception: For any other unexpected error.
    """
    image_data = load_image(image_path)

    # Extract LSB data
    lsb_data = __extract_lsb_data(image_data)

    # Read and convert integers to Unicode characters until
    # hitting a non-printable character or the delimiter
    message_bytes = __process_extracted_data(lsb_data)

    # Decrypt if its specified
    if password:
        return decrypt_message(message_bytes, password).decode()
    else:
        return message_bytes.decode()
