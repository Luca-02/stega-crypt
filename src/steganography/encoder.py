from typing import Optional

from src.config import DEFAULT_OUTPUT_DIR
from src.service import EncodeRequest, create_default_service


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
    return create_default_service().encode(
        EncodeRequest(
            image_path=image_path,
            message=message,
            message_path=message_path,
            output_path=output_path,
            image_name=image_name,
            compress=compress,
            password=password,
        )
    )
