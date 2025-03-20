import numpy as np
from PIL import Image, UnidentifiedImageError


def load_message(message_path: str) -> str:
    """
    Load a text file containing the message and return the message text.

    :param message_path: The path to the message file.
    :return: The message data as a string.
    :raises FileNotFoundError: If the message file does not exist.
    """
    try:
        with open(message_path, "r") as text:
            message = text.read()
        return message
    except FileNotFoundError:
        raise FileNotFoundError(f'The file \'{message_path}\' was not found. Please verify the path.')
    except Exception as e:
        raise Exception(f'An unexpected error occurred while loading message {message_path}: {e}')


def load_image(image_path: str) ->  tuple[np.ndarray, tuple[int, int]]:
    """
    Load an image and return the image data.

    :param image_path: The path to the image file.
    :return: The image data as a numpy array and its size.
    :raises FileNotFoundError: If the image file does not exist.
    :raises UnidentifiedImageError: If the image file is invalid or corrupted.
    """
    try:
        with Image.open(image_path) as img:
            data = np.array(img)
        return data, img.size
    except FileNotFoundError:
        raise FileNotFoundError(f'The file \'{image_path}\' was not found. Please verify the path.')
    except UnidentifiedImageError:
        raise UnidentifiedImageError(f'The file \'{image_path}\' is not a valid image or is corrupt.')
    except Exception as e:
        raise Exception(f'An unexpected error occurred while loading image {image_path}: {e}')
