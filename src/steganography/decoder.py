from typing import Optional

import numpy as np

from src.config import DELIMITER_SUFFIX
from src.cryptography.decrypt import decrypt_message
from src.logger import logger
from src.steganography.compressor import decompress_message
from src.steganography.file_handler import load_image


def __extract_lsb_data(image_data: np.ndarray) -> np.ndarray:
    """
    Extract the least significant bits from the image data.

    :param image_data: NumPy array of image data.
    :return: NumPy array of extracted LSB bits.
    """
    logger.debug(f"Extracting LSB from image data: shape={image_data.shape}")

    # Flatten the pixel arrays
    flat_data = image_data.flatten()

    # Extract just the least significant bit from each byte
    lsb_bits = flat_data & 1

    return lsb_bits


def __process_extracted_data(lsb_data: np.ndarray) -> bytes:
    """
    Process extracted data retrieving the hidden data, handling
    compression if present.

    :param lsb_data: Raw extracted data from the image LSB.
    :return: Processed data, decompressed if needed.
    """
    logger.debug(f"Processing extracted LSB data: {len(lsb_data)} bits")

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
    logger.debug(f"Extracted message bytes: {len(message_bytes)} bytes")
    return decompress_message(message_bytes)


def decode_message(
    image_path: str,
    password: Optional[str] = None,
) -> str:
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
    logger.info(f"Starting message decoding: image_path={image_path}")
    image_data = load_image(image_path)
    logger.debug(
        f"Image loaded: shape={image_data.shape}, type={image_data.dtype}"
    )

    # Extract LSB data
    lsb_data = __extract_lsb_data(image_data)
    logger.debug(f"Extracted LSB data: {len(lsb_data)} bits")

    # Read and convert integers to Unicode characters until
    # hitting a non-printable character or the delimiter
    message_bytes = __process_extracted_data(lsb_data)

    # Decrypt if its specified
    if password:
        logger.info("Decrypting message")
        return decrypt_message(message_bytes, password).decode()
    else:
        logger.info("No password provided, decoding without decryption")
        return message_bytes.decode()
