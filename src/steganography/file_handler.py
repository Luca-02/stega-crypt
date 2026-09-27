import os

from src.exceptions import FileAlreadyExistsError, MessageFileNotFoundError
from src.logger import logger


def ensure_file_does_not_exist(output_path: str, file_name: str) -> None:
    """Check that the output file does not exist yet.

    Args:
        output_path: Directory the file will be saved in.
        file_name: Full path of the file to check.

    Raises:
        FileAlreadyExistsError: If the file already exists.
    """
    if os.path.isdir(output_path) and os.path.isfile(file_name):
        raise FileAlreadyExistsError(
            f'The file "{file_name}" already exists in the directory "{output_path}".'
        )


def ensure_directory_exists(directory: str) -> None:
    """Create the directory if it does not exist.

    Args:
        directory: The directory to check.
    """
    if not os.path.exists(directory):
        logger.debug(f"Creating output directory: {directory}")
        os.makedirs(directory)


def load_message_file(message_path: str) -> str:
    """Load a text file containing the message.

    Args:
        message_path: The path to the message file.

    Returns:
        The message data as a string.

    Raises:
        MessageFileNotFoundError: If the message file does not exist.
        Exception: For any other unexpected error.
    """
    logger.info(f"Loading message from file: {message_path}")

    try:
        with open(message_path, "r") as text:
            message = text.read()

        logger.debug(
            f"Message loaded successfully: length={len(message)} characters"
        )
        return message
    except FileNotFoundError:
        raise MessageFileNotFoundError(
            f'The file "{message_path}" was not found, please verify the path.'
        )
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred while loading message {message_path}: {e}"
        )


def save_message_file(
    message: str,
    output_path: str,
    file_name: str,
) -> str:
    """Save a message as a UTF-8 text file.

    Args:
        message: The message to save.
        output_path: Directory to save the message in.
        file_name: Name of the output file, without extension.

    Returns:
        Path to the saved file.

    Raises:
        FileAlreadyExistsError: If the output file already exists.
        Exception: For any other unexpected error.
    """
    file = f"{file_name}.txt"
    output_file_path = os.path.join(output_path, f"{file}")

    logger.info(f"Saving message: {output_file_path}")

    ensure_file_does_not_exist(output_path, output_file_path)

    try:
        ensure_directory_exists(output_path)
        with open(output_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(message)

        logger.info(f"Message saved successfully into {output_file_path}")
        return output_file_path
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred while saving image {output_file_path}: {e}"
        )
