import os
from typing import Optional

import numpy as np
from PIL import Image

from config import DEFAULT_OUTPUT_DIR, COMPRESSION_PREFIX, DELIMITER_SUFFIX
from steganography.compressor import compress_message
from utils.file_handler import load_image, load_message
from cryptography.encrypt import encrypt_data


def __create_hidden_message(message: str, password: str, compression: bool) -> bytes:
    """
    Prepare the message to hide, with or without compression.

    :param message: The plaintext message.
    :param password: If different then None, apply encryption with it.
    :param compression: If True, apply compression. If False, no compression.
    If None, automatically choose the most efficient option.
    :return: The message ready to be hidden in the image.
    """
    if password:
        data = encrypt_data(message.encode(), password)
    else:
        data = message.encode()

    hidden_message = data + DELIMITER_SUFFIX.encode()
    if compression is False:
        return hidden_message

    compressed_message = COMPRESSION_PREFIX.encode() + compress_message(data) + DELIMITER_SUFFIX.encode()
    if compression or len(compressed_message) < len(hidden_message):
        return compressed_message

    return hidden_message


def __bytes_to_bits_binary_list(byte_data: bytes) -> list[int]:
    """
    Converts a bytes object into a list of binary bits.

    :param byte_data: Bytes object.
    :return: The corresponding list of binary bits.
    """
    return [int(bit) for bit in ''.join(f'{byte:08b}' for byte in byte_data)]


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


def encode_message(
        image_path: str,
        message: Optional[str] = None,
        message_path: Optional[str] = None,
        output_path: Optional[str] = DEFAULT_OUTPUT_DIR,
        new_image_name: Optional[str] = None,
        password: Optional[str] = None,
        compress: Optional[bool] = None
) -> None:
    """
    Encodes a hidden compressed message into an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the input image.
    :param message: Message to hide (if not using a text file).
    :param message_path: Path to the text file containing the message (optional).
    :param output_path: The output folder to save the modified image. Default is './.output'.
    :param new_image_name: The name of the new image file.
    If not specified, '-modified' is appended to the original name.
    :param password: The password to encrypt the hidden message.
    If not specified the message will not be encrypted.
    :param compress: Boolean value to indicate whether to compress the message.
    If not specified it will be
    automatically compressed if it is convenient with respect to the weight of the compressed message.
    :raises FileNotFoundError: If the message or image file is not found.
    :raises ValueError: If the message is empty or is too large to fit in the image.
    :raises FileExistsError: If the output file already exists.
    :raises Exception: For any other unexpected error.
    """
    if message_path:
        message = load_message(message_path)

    # Validate message
    if not message:
        raise ValueError('You can\'t use an empty message.')

    image_data, (width, height) = load_image(image_path)

    # Create the hidden message
    hidden_message = __create_hidden_message(message, password, compress)

    # Convert to bit array
    binary_message = __bytes_to_bits_binary_list(hidden_message)

    # Flatten the pixel arrays
    flat_data = image_data.flatten()

    if len(binary_message) > len(flat_data):
        raise ValueError(f'Message too large! ({len(binary_message)} bit) - Maximum capacity: {len(flat_data)} bit.')

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
        raise FileExistsError(f'The file \'{new_image_name}\' already exists in the directory \'{output_path}\'.')

    # Create and save the new image with the hidden message
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    new_img = Image.fromarray(modified_data)
    try:
        new_img.save(output_file_path, format=file_extension.upper())
    except Exception as e:
        raise Exception(f'An unexpected error occurred while saving image {output_file_path}: {e}')
