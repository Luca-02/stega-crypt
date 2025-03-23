import os

import numpy as np
from PIL import Image, UnidentifiedImageError

from src.exceptions import (
    FileAlreadyExistsError,
    ImageFileNotFoundError,
    MessageFileNotFoundError,
)


def load_message(message_path: str) -> str:
    """
    Load a text file containing the message and return the message text.

    :param message_path: The path to the message file.
    :return: The message data as a string.
    :raises MessageFileNotFoundError: If the message file does not exist.
    """
    try:
        with open(message_path, "r") as text:
            message = text.read()
        return message
    except FileNotFoundError:
        raise MessageFileNotFoundError(
            f"The file '{message_path}' was not found. Please verify the path."
        )
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred while loading message {message_path}: {e}"
        )


def load_image(image_path: str) -> np.ndarray:
    """
    Load an image and return the image data.

    :param image_path: The path to the image file.
    :return: The image data as a numpy array.
    :raises ImageFileNotFoundError: If the image file does not exist.
    :raises UnidentifiedImageError: If the image file is invalid or corrupted.
    """
    try:
        with Image.open(image_path) as img:
            return np.array(img)
    except FileNotFoundError:
        raise ImageFileNotFoundError(
            f"The file '{image_path}' was not found. Please verify the path."
        )
    except UnidentifiedImageError:
        raise UnidentifiedImageError(
            f"The file '{image_path}' is not a valid image or is corrupt."
        )
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred while loading image {image_path}: {e}"
        )


def save_image(
    image_data: np.ndarray,
    output_path: str,
    image_name: str,
    image_format: str,
) -> str:
    """
    Save an image to the specified path.

    :param image_data: NumPy array containing image data.
    :param output_path: Directory to save the image in.
    :param image_name: Name of the output file.
    :param image_format: Image format to save as.
    :return: Path to the saved file.
    :raises FileAlreadyExistsError: If the file couldn't be saved.
    """
    new_image = f"{image_name}.{image_format}"
    output_file_path = os.path.join(output_path, f"{new_image}")

    # Check if the output file already exists
    if os.path.isdir(output_path) and os.path.isfile(output_file_path):
        raise FileAlreadyExistsError(
            f"The file '{new_image}' already exists in the directory '{output_path}'."
        )

    try:
        # Create and save the new image with the hidden message
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        new_img = Image.fromarray(image_data)
        new_img.save(output_file_path, format=image_format)
        return output_file_path
    except Exception as e:
        raise Exception(
            f"An unexpected error occurred while saving image {output_file_path}: {e}"
        )
