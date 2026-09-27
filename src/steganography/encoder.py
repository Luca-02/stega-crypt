import os
from typing import Optional

from src.config import DEFAULT_OUTPUT_DIR, MODIFIED_IMAGE_SUFFIX
from src.cryptography.aes_gcm import AesGcmCipher
from src.exceptions import InputMessageConflictError, NoMessageFoundError
from src.logger import logger
from src.steganography.file_handler import load_message_file
from src.steganography.image_store import PillowImageStore
from src.steganography.lsb import SequentialLsbStrategy
from src.steganography.payload_codec import PayloadCodec


def encode_message(
    image_path: str,
    message: Optional[str] = None,
    message_path: Optional[str] = None,
    output_path: Optional[str] = DEFAULT_OUTPUT_DIR,
    image_name: Optional[str] = None,
    compress: Optional[bool] = True,
    password: Optional[str] = None,
) -> str:
    """Hide a message into an image with the Least Significant Bit technique.

    Args:
        image_path: The path to the input image.
        message: Message to hide, when not using a text file.
        message_path: Path to the text file containing the message.
        output_path: The output folder to save the modified image.
            Defaults to DEFAULT_OUTPUT_DIR.
        image_name: The name of the new image file. If not specified,
            '-modified' is appended to the original name.
        compress: Whether to compress the message. When True, the message
            is compressed only if that makes it smaller.
        password: The password to encrypt the hidden message. If not
            specified, the message is not encrypted.

    Returns:
        Path to the new image file with the embedded hidden message.

    Raises:
        InputMessageConflictError: If both message and message_path are
            given.
        MessageFileNotFoundError: If the message file is not found.
        NoMessageFoundError: If the message is empty.
        ImageFileNotFoundError: If the image file is not found.
        InvalidPasswordError: If the password is not valid.
        MessageTooLargeError: If the message is too large to fit in the
            image.
        FileAlreadyExistsError: If the output file already exists.
        Exception: For any other unexpected error.
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

    image_store = PillowImageStore()
    image_data = image_store.load(image_path)
    logger.debug(
        f"Image loaded: shape={image_data.shape}, type={image_data.dtype}"
    )

    # Create the hidden message
    codec = PayloadCodec(AesGcmCipher())
    hidden_message = codec.encode(message, password, compress)
    logger.debug(f"Hidden message prepared: size={len(hidden_message)} bytes")

    # Embed message in image
    strategy = SequentialLsbStrategy()
    modified_image = strategy.embed(image_data, hidden_message)

    # If the modified image name is not specified, add "-modified" to the original name
    if image_name is None:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        image_name = f"{base_name}{MODIFIED_IMAGE_SUFFIX}"

    # Determines the extent of the input image
    image_format = os.path.splitext(image_path)[1].lower().strip(".")

    logger.info(f"Saving modified image: {image_name}.{image_format}")
    return image_store.save(
        modified_image, output_path, image_name, image_format
    )
