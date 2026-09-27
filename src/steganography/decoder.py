from typing import Optional

from src.config import DEFAULT_OUTPUT_DIR
from src.service import DecodeRequest, create_default_service


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
    return create_default_service().decode(
        DecodeRequest(
            image_path=image_path,
            output_path=output_path,
            message_name=message_name,
            save_message=save_message,
            password=password,
        )
    )
