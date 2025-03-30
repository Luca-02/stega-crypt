import os

import numpy as np
from PIL import Image, UnidentifiedImageError

from src.exceptions import (
    FileAlreadyExistsError,
    ImageFileNotFoundError,
    MessageFileNotFoundError,
)
from src.logger import logger


def __ensure_file_doesnt_exists(output_path: str, file_name: str):
    """
    Check if the output file already exists

    :raises FileAlreadyExistsError: If the file couldn't be saved.
    """
    if os.path.isdir(output_path) and os.path.isfile(file_name):
        raise FileAlreadyExistsError(
            f'The file "{file_name}" already exists in the directory "{output_path}".'
        )


def __ensure_directory_exists(directory: str):
    """
    Check if the folder exists, otherwise create it.
    """
    if not os.path.exists(directory):
        logger.debug(f"Creating output directory: {directory}")
        os.makedirs(directory)


def load_message_file(message_path: str) -> str:
    """
    Load a text file containing the message and return the message text.

    :param message_path: The path to the message file.
    :return: The message data as a string.
    :raises MessageFileNotFoundError: If the message file does not exist.
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
):
    """
    Save a message to the specified path.

    :param message: Simple string.
    :param output_path: Directory to save the message in.
    :param file_name: Name of the output file.
    :return: Path to the saved file.
    :raises FileAlreadyExistsError: If the file couldn't be saved.
    """
    file = f"{file_name}.txt"
    output_file_path = os.path.join(output_path, f"{file}")

    logger.info(f"Saving message: {output_file_path}")

    __ensure_file_doesnt_exists(output_path, output_file_path)

    try:
        __ensure_directory_exists(output_path)
        with open(output_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(message)

        logger.info(f"Message saved successfully into {output_file_path}")
        return output_file_path
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred while saving image {output_file_path}: {e}"
        )


def load_image_file(image_path: str) -> np.ndarray:
    """
    Load an image and return the image data.

    :param image_path: The path to the image file.
    :return: The image data as a numpy array.
    :raises ImageFileNotFoundError: If the image file does not exist.
    :raises UnidentifiedImageError: If the image file is invalid or corrupted.
    """
    logger.info(f"Loading image: {image_path}")

    try:
        with Image.open(image_path) as img:
            image_array = np.array(img)
            logger.debug(
                f"Image loaded successfully: "
                f"shape={image_array.shape}, type={image_array.dtype}"
            )
            return image_array

    except FileNotFoundError:
        raise ImageFileNotFoundError(
            f'The file "{image_path}" was not found, please verify the path.'
        )
    except UnidentifiedImageError:
        raise UnidentifiedImageError(
            f'The file "{image_path}" is not a valid image or is corrupt.'
        )
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred while loading image {image_path}: {e}"
        )


def save_image_file(
    image_data: np.ndarray,
    output_path: str,
    file_name: str,
    file_format: str,
) -> str:
    """
    Save an image to the specified path.

    :param image_data: NumPy array containing image data.
    :param output_path: Directory to save the image in.
    :param file_name: Name of the output file.
    :param file_format: Image format to save as.
    :return: Path to the saved file.
    :raises FileAlreadyExistsError: If the file couldn't be saved.
    """
    file = f"{file_name}.{file_format}"
    output_file_path = os.path.join(output_path, f"{file}")

    logger.info(f"Saving image: {output_file_path}")

    __ensure_file_doesnt_exists(output_path, output_file_path)

    try:
        __ensure_directory_exists(output_path)
        new_img = Image.fromarray(image_data)
        new_img.save(output_file_path, format=file_format)

        logger.info(f"Image saved successfully into {output_file_path}")
        return output_file_path
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred while saving image {output_file_path}: {e}"
        )
