import os
from typing import Optional

import numpy as np

from src.config import (
    DEFAULT_OUTPUT_DIR,
    DELIMITER_SUFFIX,
    MODIFIED_IMAGE_SUFFIX,
)
from src.cryptography.encrypt import encrypt_data
from src.exceptions import (
    InputMessageConflictError,
    MessageTooLargeError,
    NoMessageFoundError,
)
from src.logger import logger
from src.steganography.compressor import compress_message
from src.steganography.file_handler import (
    load_image_file,
    load_message_file,
    save_image_file,
)


def __create_hidden_message(
    message: str,
    password: str,
    compression: bool,
) -> bytes:
    """
    Prepare the message to hide, with or without compression.

    :param message: The plaintext message.
    :param password: If different then None, apply encryption with it.
    :param compression: If True, apply compression if it's convenient.
    :return: The message ready to be hidden in the image.
    """
    logger.debug(
        f"Creating hidden message: "
        f"compression={compression}, password_provided={bool(password)}"
    )

    if password:
        logger.debug("Encrypting message")
        data = encrypt_data(message.encode(), password)
    else:
        data = message.encode()

    hidden_message: bytes
    if compression is False:
        hidden_message = data
        logger.debug("No compression applied")
    else:
        hidden_message = compress_message(data)
        logger.debug("Message compressed")

    return hidden_message + DELIMITER_SUFFIX.encode()


def __bytes_to_bits_binary_list(byte_data: bytes) -> np.ndarray:
    """
    Converts bytes data to a bit array.

    :param byte_data: Bytes to convert.
    :return: NumPy array of bits (0s and 1s).
    """
    logger.debug(f"Converting {len(byte_data)} bytes to binary list")
    return np.unpackbits(np.frombuffer(byte_data, dtype=np.uint8))


def __modify_lsb(flat_data: np.ndarray, b_message: np.ndarray) -> None:
    """
    Change the least significant bits (LSB) of the pixels to the message bits.

    :param flat_data: Flattened NumPy array of image pixels.
    :param b_message: NumPy array of binary bits representing the message.
    """
    logger.debug(
        f"Modifying LSB of {len(flat_data)} pixels with {len(b_message)} message bits"
    )
    target_data = flat_data[: len(b_message)]

    # Set the LSBs to 0 and then insert message bits
    target_data = target_data & ~np.uint8(1) | b_message

    flat_data[: len(b_message)] = target_data


def __add_noise(flat_data: np.ndarray, used_bits: int) -> None:
    """
    Adds random noise to unused LSB bits in the image to prevent detection.

    :param flat_data: NumPy array representing the image data.
    :param used_bits: Number of bits used for message encoding.
    """
    logger.debug(f"Adding noise to {len(flat_data) - used_bits} unused bits")
    unused_data = flat_data[used_bits:]

    # Generate a random binary mask (0 or 1) for flipping LSBs
    noise_mask = np.random.choice(
        [0, 1], size=unused_data.shape, p=[0.7, 0.3]
    ).astype(np.uint8)

    # Apply the noise mask using XOR (flips LSB randomly)
    unused_data ^= noise_mask

    flat_data[used_bits:] = unused_data


def __embed_hidden_message_in_image(
    image_data: np.ndarray,
    binary_message: np.ndarray,
) -> np.ndarray:
    """
    Embed message bits into the LSB of the image pixels adding some random noise.

    :param image_data: NumPy array of image data.
    :param binary_message: NumPy array of message binary bits.
    :return: Modified image data with embedded message.
    :raises MessageTooLargeError: If the message doesn't fit in the image.
    """
    # Flatten the pixel arrays
    flat_data = image_data.flatten()

    logger.info(f"Embedding message: size={len(binary_message)} bits")

    # Check if message will fit
    if len(binary_message) > len(flat_data):
        raise MessageTooLargeError(
            f"Message too large! ({len(binary_message)} bit) "
            f"- Max capacity: {len(flat_data)} bit."
        )

    # Add message and random noise
    __modify_lsb(flat_data, binary_message)
    __add_noise(flat_data, len(binary_message))

    # Reshape back to an image pixel array
    return np.reshape(flat_data, image_data.shape)


def encode_message(
    image_path: str,
    message: Optional[str] = None,
    message_path: Optional[str] = None,
    output_path: Optional[str] = DEFAULT_OUTPUT_DIR,
    image_name: Optional[str] = None,
    compress: Optional[bool] = True,
    password: Optional[str] = None,
) -> str:
    """
    Encodes a hidden compressed message into an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the input image.
    :param message: Message to hide (if not using a text file).
    :param message_path: Path to the text file containing the message (optional).
    :param output_path: The output folder to save the modified image. Default is the current path.
    :param image_name: The name of the new image file.
    If not specified, '-modified' is appended to the original name.
    :param compress: Boolean value to indicate whether to compress the message.
    If It's true, it will be automatically compressed if it is convenient with respect to the weight
    of the compressed message.
    :param password: The password to encrypt the hidden message.
    If not specified the message will not be encrypted.
    :return: Path to the new image file with the embedded hidden message.
    :raises InputMessageConflictError: If there is an input message conflict receiving both
    message and message_path.
    :raises MessageFileNotFoundError: If the message is not found.
    :raises ImageFileNotFoundError: If the image file is not found.
    :raises NoMessageFoundError: If the message is empty.
    :raises MessageTooLargeError: If the message is too large to fit in the image.
    :raises FileAlreadyExistsError: If the output file already exists.
    :raises Exception: For any other unexpected error.
    """
    logger.info(f"Starting message encoding: image_path={image_path}")

    if message and message_path:
        raise InputMessageConflictError(
            "Input message conflict, choose whether to use a string or a text file"
        )

    if message_path:
        logger.info(f"Loading message from file: {message_path}")
        message = load_message_file(message_path)

    # Validate message
    if not message:
        raise NoMessageFoundError("You can't use an empty message.")

    logger.info(f"Message loaded: {len(message)} characters")

    image_data = load_image_file(image_path)
    logger.debug(
        f"Image loaded: shape={image_data.shape}, type={image_data.dtype}"
    )

    # Create the hidden message
    hidden_message = __create_hidden_message(message, password, compress)
    logger.debug(f"Hidden message prepared: size={len(hidden_message)} bytes")

    # Convert to bit array
    binary_message = __bytes_to_bits_binary_list(hidden_message)

    # Embed message in image
    modified_image = __embed_hidden_message_in_image(
        image_data, binary_message
    )

    # If the modified image name is not specified, add "-modified" to the original name
    if image_name is None:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        image_name = f"{base_name}{MODIFIED_IMAGE_SUFFIX}"

    # Determines the extent of the input image
    image_format = os.path.splitext(image_path)[1].lower().strip(".")

    logger.info(f"Saving modified image: {image_name}.{image_format}")
    return save_image_file(
        modified_image, output_path, image_name, image_format
    )
