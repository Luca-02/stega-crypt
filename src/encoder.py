import os
from typing import Optional

import numpy as np
from PIL import Image

from utility.compressor import compress_message
from config import DELIMITER
from config import OUTPUT_DIR
from utility.converter import bytes_to_bits_binary_list
from utility.file_handler import load_image, load_message


def __modify_lsb(flat_data: np.ndarray, b_message: list[int]) -> None:
    """
    Change the least significant bits (LSB) of the pixels to the message bits.

    :param flat_data: Flattened NumPy array of image pixels.
    :param b_message: List of binary bits representing the message.
    """

    target_data = flat_data[:len(b_message)]

    # Set the LSBs to 0 and then insert message bits
    target_data = target_data & ~np.uint8(1) | b_message

    flat_data[:len(b_message)] = target_data


def __add_noise(flat_data: np.ndarray, used_bits: int) -> None:
    """
    Adds random noise to unused LSB bits in the image to prevent detection.

    :param flat_data: NumPy array representing the image data.
    :param used_bits: Number of bits used for message encoding.
    """
    unused_data = flat_data[used_bits:]

    # Generate a random binary mask (0 or 1) for flipping LSBs
    noise_mask = np.random.randint(2, size=unused_data.shape, dtype=np.uint8)

    # Apply the noise mask using XOR (flips LSB randomly)
    unused_data ^= noise_mask

    flat_data[used_bits:] = unused_data


def encode_message_from_file(
        image_path: str,
        message_path: str,
        output_path: str = OUTPUT_DIR,
        new_image_name: Optional[str] = None
) -> None:
    """
    Encodes a hidden message from a text file into an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the input image.
    :param message_path: Path to a text file containing the message.
    :param output_path: The output folder to save the modified image. Default is './.output'.
    :param new_image_name: The name of the new image file. If not specified, '-modified' is appended to the original name.

    :raises FileNotFoundError: If the image file is not found.
    :raises ValueError: If the message is too large to fit in the image.
    :raises FileExistsError: If the output file already exists.
    :raises Exception: For any other unexpected error.
    """
    message = load_message(message_path)

    encode_message(image_path, message, output_path, new_image_name)


def encode_message(
        image_path: str,
        message: str,
        output_path: str = OUTPUT_DIR,
        new_image_name: Optional[str] = None
) -> None:
    """
    Encodes a hidden compressed message into an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the input image.
    :param message: The message to be hidden within the image.
    :param output_path: The output folder to save the modified image. Default is './.output'.
    :param new_image_name: The name of the new image file. If not specified, '-modified' is appended to the original name.

    :raises FileNotFoundError: If the image file is not found.
    :raises ValueError: If the message is too large to fit in the image.
    :raises FileExistsError: If the output file already exists.
    :raises Exception: For any other unexpected error.
    """
    # Validate message
    if not message:
        raise ValueError("You can't use an empty message.")

    image_data, (width, height) = load_image(image_path)

    # Add delimiter to message
    compressed_message = compress_message(message.encode()) + DELIMITER.encode()

    # Convert to bit array
    binary_message = bytes_to_bits_binary_list(compressed_message)

    # Flatten the pixel arrays
    flat_data = image_data.flatten()

    if len(binary_message) > len(flat_data):
        raise ValueError(
            f"Message too large! ({len(binary_message)} bit) - Maximum capacity: {len(flat_data)} bit.")

    # Add message and random noise
    __modify_lsb(flat_data, binary_message)
    __add_noise(flat_data, len(binary_message))

    # Reshape back to an image pixel array
    modified_data = np.reshape(flat_data, (width, height, 3))

    # If the modified image name is not specified, add "-modified" to the original name
    if new_image_name is None:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        new_image_name = f"{base_name}-modified"

    # Determines the extent of the input image
    file_extension = os.path.splitext(image_path)[1].lower().strip(".")
    new_image_name = f"{new_image_name}.{file_extension}"

    output_file_path = os.path.join(output_path, f"{new_image_name}")

    # Check if the output file already exists
    if os.path.isdir(output_path) and os.path.isfile(output_file_path):
        raise FileExistsError(f"The file '{new_image_name}' already exists in the directory '{output_path}'.")

    # Create and save the new image with the hidden message
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    new_img = Image.fromarray(modified_data)
    try:
        new_img.save(output_file_path, format=file_extension.upper())
    except Exception as e:
        raise Exception(f"An unexpected error occurred while saving image {output_file_path}: {e}")
