import os
from typing import Optional

from src.config import DEFAULT_OUTPUT_DIR, MESSAGE_NAME_SUFFIX
from src.cryptography.aes_gcm import AesGcmCipher
from src.logger import logger
from src.steganography.file_handler import save_message_file
from src.steganography.image_store import PillowImageStore
from src.steganography.lsb import SequentialLsbStrategy
from src.steganography.payload_codec import PayloadCodec


def decode_message(
    image_path: str,
    output_path: Optional[str] = DEFAULT_OUTPUT_DIR,
    message_name: Optional[str] = None,
    save_message: Optional[bool] = False,
    password: Optional[str] = None,
) -> str:
    """Extract a hidden message from an image with the LSB technique.

    Args:
        image_path: The path to the image containing the hidden message.
        output_path: The output folder to save the message. Defaults to
            DEFAULT_OUTPUT_DIR.
        message_name: The name of the message file. If not specified, it
            will be '<image_name>-message'.
        save_message: Whether to save the message to a file.
        password: The password to decrypt the hidden message. If not
            specified, the message is not decrypted.

    Returns:
        The hidden message, or the path of the saved message file when
        save_message is True.

    Raises:
        ImageFileNotFoundError: If the image file is not found.
        UnidentifiedImageError: If the file is not a valid image.
        InvalidPasswordError: If the password is not valid.
        DecryptionError: If the password is wrong or the data is corrupted.
        FileAlreadyExistsError: If the message file already exists.
        Exception: For any other unexpected error.
    """
    logger.info(f"Starting message decoding: image_path={image_path}")
    image_store = PillowImageStore()
    image_data = image_store.load(image_path)
    logger.debug(
        f"Image loaded: shape={image_data.shape}, type={image_data.dtype}"
    )

    # Extract the raw byte stream hidden in the image and let the payload
    # codec decode the message
    strategy = SequentialLsbStrategy()
    packed_bytes = strategy.extract(image_data)

    codec = PayloadCodec(AesGcmCipher())
    message = codec.decode(packed_bytes, password)

    if not save_message:
        return message

    # Determine file name if not specified
    if message_name is None:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        message_name = f"{base_name}{MESSAGE_NAME_SUFFIX}"

    # Save message if output_path specified
    logger.info(f"Saving message: {message_name}.txt")
    return save_message_file(message, output_path, message_name)
