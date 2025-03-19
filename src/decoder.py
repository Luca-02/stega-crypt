import numpy as np

from utility.compressor import decompress_message
from config import DELIMITER
from utility.file_handler import load_image


def decode_message(image_path: str) -> str:
    """
    Extracts the hidden message from an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the image containing the hidden message.

    :return: The hidden message extracted from the image.

    :raises FileNotFoundError: If the image file is not found.
    :raises UnidentifiedImageError: If the file is not a valid image.
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
    message = b''
    for pack in pack_data:
        message += int(pack).to_bytes()

        # If the message ends with the delimiter, remove it and break
        if message.endswith(DELIMITER.encode()):
            message = message[:-len(DELIMITER)]
            break

    return decompress_message(message).decode()
