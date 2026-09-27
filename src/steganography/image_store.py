import os
from typing import Protocol

import numpy as np
from PIL import Image, UnidentifiedImageError

from src.exceptions import ImageFileNotFoundError
from src.logger import logger
from src.steganography.file_handler import (
    ensure_directory_exists,
    ensure_file_does_not_exist,
)


class ImageStore(Protocol):
    """Common interface for loading and saving image pixel data."""

    def load(self, image_path: str) -> np.ndarray:
        """Load an image as a NumPy array.

        Args:
            image_path: The path to the image file.

        Returns:
            The image data as a NumPy array.

        Raises:
            ImageFileNotFoundError: If the image file does not exist.
            UnidentifiedImageError: If the image file is invalid or
                corrupted.
            Exception: For any other unexpected error.
        """
        ...

    def save(
        self,
        pixels: np.ndarray,
        output_path: str,
        file_name: str,
        image_format: str,
    ) -> str:
        """Save pixel data as an image file.

        Args:
            pixels: NumPy array containing image data.
            output_path: Directory to save the image in.
            file_name: Name of the output file, without extension.
            image_format: Image format to save as, also used as
                extension.

        Returns:
            Path to the saved file.

        Raises:
            FileAlreadyExistsError: If the output file already exists.
            Exception: For any other unexpected error.
        """
        ...


class PillowImageStore:
    """Image store backed by Pillow, reading and writing pixels as arrays."""

    def load(self, image_path: str) -> np.ndarray:
        """Load an image as a NumPy array.

        Args:
            image_path: The path to the image file.

        Returns:
            The image data as a NumPy array.

        Raises:
            ImageFileNotFoundError: If the image file does not exist.
            UnidentifiedImageError: If the image file is invalid or
                corrupted.
            Exception: For any other unexpected error.
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

    def save(
        self,
        pixels: np.ndarray,
        output_path: str,
        file_name: str,
        image_format: str,
    ) -> str:
        """Save pixel data as an image file.

        Args:
            pixels: NumPy array containing image data.
            output_path: Directory to save the image in.
            file_name: Name of the output file, without extension.
            image_format: Image format to save as, also used as
                extension.

        Returns:
            Path to the saved file.

        Raises:
            FileAlreadyExistsError: If the output file already exists.
            Exception: For any other unexpected error.
        """
        file = f"{file_name}.{image_format}"
        output_file_path = os.path.join(output_path, f"{file}")

        logger.info(f"Saving image: {output_file_path}")

        ensure_file_does_not_exist(output_path, output_file_path)

        try:
            ensure_directory_exists(output_path)
            new_img = Image.fromarray(pixels)
            new_img.save(output_file_path, format=image_format)

            logger.info(f"Image saved successfully into {output_file_path}")
            return output_file_path
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while saving image {output_file_path}: {e}"
            )
