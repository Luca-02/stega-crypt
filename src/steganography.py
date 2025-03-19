import os
from typing import Optional

import numpy as np
from PIL import Image, UnidentifiedImageError

from config import OUTPUT_DIR, DELIMITER


def __load_image(image_path: str):
    """
    Helper function to load an image and return the image data.

    :param image_path: The path to the image file.
    :return: The image data as a numpy array.
    :raises FileNotFoundError: If the image file does not exist.
    :raises UnidentifiedImageError: If the image file is invalid or corrupted.
    """
    try:
        with Image.open(image_path) as img:
            data = np.array(img)
        return data, img.size
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{image_path}' was not found. Please verify the path.")
    except UnidentifiedImageError:
        raise UnidentifiedImageError(f"The file '{image_path}' is not a valid image or is corrupt.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while loading image {image_path}: {e}")


def encode(
        image_path: str,
        message: str,
        output_path: str = OUTPUT_DIR,
        new_image_name: Optional[str] = None
) -> None:
    """
    Hides a message within an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the input image.
    :param message: The message to be hidden within the image.
    :param output_path: The output folder to save the modified image. Default is './.output'.
    :param new_image_name: The name of the new image file. If not specified, '-modified' is appended to the original name.
    :raises FileNotFoundError: If the image file is not found.
    :raises ValueError: If the message is too large to fit in the image.
    :raises FileExistsError: If the output file already exists.
    :raises Exception: For any other unexpected error.
    """
    # Validate the message
    if not message:
        raise ValueError("You can't use an empty message.")

    # Load image and check its size
    data, (width, height) = __load_image(image_path)

    # Add delimiter to message
    message += DELIMITER

    # Encode the message in a series of 8-bit values
    b_message = ''.join(format(ord(i), '08b') for i in message)
    b_message = [int(x) for x in b_message]

    # Flatten the pixel arrays
    flat_data = data.flatten()

    if len(b_message) > len(flat_data):
        raise ValueError(f"Message too large! ({len(b_message)} bit) - Maximum capacity: {len(flat_data)} bit.")

    # Overwrite pixel LSB
    flat_data[:len(b_message)] = (flat_data[:len(b_message)] & np.uint8(~np.uint8(1))) | b_message

    # Reshape back to an image pixel array
    modified_data = np.reshape(flat_data, (height, width, 3))

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
        raise FileExistsError(f"The file '{new_image_name}' already exists in the directory '{output_path}'.")

    # Create and save the new image with the hidden message
    new_img = Image.fromarray(modified_data)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        new_img.save(output_file_path, format=file_extension.upper())
    except Exception as e:
        raise Exception(f"An unexpected error occurred while saving image {output_file_path}: {e}")


def decode(image_path: str) -> str:
    """
    Extracts the hidden message from an image using the Least Significant Bit (LSB) technique.

    :param image_path: The path to the image containing the hidden message.
    :return: The hidden message extracted from the image.
    :raises FileNotFoundError: If the image file is not found.
    :raises UnidentifiedImageError: If the file is not a valid image.
    :raises Exception: For any other unexpected error.
    """
    # Load image
    data, _ = __load_image(image_path)

    # Flatten the pixel arrays
    data = data.flatten()

    # Extract Least-Significant-Bit
    data = data & 1

    # Packs binary-valued array into 8-bits array.
    data = np.packbits(data)

    # Read and convert integers to Unicode characters until hitting a non-printable character or the delimiter
    message = ""
    for byte in data:
        char = chr(byte)
        if not char.isprintable():
            break
        message += char

        # If the message ends with the delimiter, remove it and break
        if message.endswith(DELIMITER):
            message = message[:-len(DELIMITER)]
            break

    return message
