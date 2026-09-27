import os
from tempfile import TemporaryDirectory
from unittest import TestCase

import numpy as np
from PIL import Image, UnidentifiedImageError

from src.exceptions import FileAlreadyExistsError, ImageFileNotFoundError
from src.steganography.image_store import ImageStore, PillowImageStore


class TestPillowImageStore(TestCase):
    def setUp(self) -> None:
        self.store: ImageStore = PillowImageStore()
        self.dir = TemporaryDirectory()
        self.img_size = (10, 10)
        self.image_path = os.path.join(self.dir.name, "img.png")

        img = Image.new("RGB", self.img_size, color=(10, 20, 30))
        img.save(self.image_path, "png")

    def tearDown(self) -> None:
        self.dir.cleanup()

    def test_load_returns_pixel_array_with_expected_shape_and_dtype(self):
        pixels = self.store.load(self.image_path)

        self.assertEqual((self.img_size[1], self.img_size[0], 3), pixels.shape)
        self.assertEqual(np.uint8, pixels.dtype)

    def test_load_missing_file_raises_image_file_not_found_error(self):
        image_path = os.path.join(self.dir.name, "missing.png")

        with self.assertRaises(ImageFileNotFoundError) as context:
            self.store.load(image_path)

        self.assertEqual(
            f'The file "{image_path}" was not found, please verify the path.',
            str(context.exception),
        )

    def test_load_non_image_file_raises_unidentified_image_error(self):
        invalid_image_path = os.path.join(self.dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError) as context:
            self.store.load(invalid_image_path)

        self.assertEqual(
            f'The file "{invalid_image_path}" is not a valid image '
            "or is corrupt.",
            str(context.exception),
        )

    def test_load_invalid_path_raises_exception(self):
        with self.assertRaises(Exception) as context:
            self.store.load("\x00")

        self.assertIs(Exception, type(context.exception))
        self.assertTrue(
            str(context.exception).startswith(
                "An unexpected error occurred while loading image"
            )
        )

    def test_save_creates_output_directory_and_returns_path(self):
        output_path = os.path.join(self.dir.name, "output_dir")
        pixels = self.store.load(self.image_path)

        saved_path = self.store.save(pixels, output_path, "saved", "png")

        self.assertEqual(os.path.join(output_path, "saved.png"), saved_path)
        self.assertTrue(os.path.isdir(output_path))

    def test_save_png_roundtrip_preserves_pixels(self):
        output_path = os.path.join(self.dir.name, "output_dir")
        pixels = self.store.load(self.image_path)

        saved_path = self.store.save(pixels, output_path, "saved", "png")
        reloaded = self.store.load(saved_path)

        np.testing.assert_array_equal(pixels, reloaded)

    def test_save_bmp_roundtrip_preserves_pixels(self):
        output_path = os.path.join(self.dir.name, "output_dir")
        pixels = self.store.load(self.image_path)

        saved_path = self.store.save(pixels, output_path, "saved", "bmp")
        reloaded = self.store.load(saved_path)

        np.testing.assert_array_equal(pixels, reloaded)

    def test_save_existing_file_raises_file_already_exists_error(self):
        output_path = os.path.join(self.dir.name, "output_dir")
        pixels = self.store.load(self.image_path)
        self.store.save(pixels, output_path, "saved", "png")

        with self.assertRaises(FileAlreadyExistsError) as context:
            self.store.save(pixels, output_path, "saved", "png")

        output_file_path = os.path.join(output_path, "saved.png")
        self.assertEqual(
            f'The file "{output_file_path}" already exists '
            f'in the directory "{output_path}".',
            str(context.exception),
        )

    def test_save_output_path_is_a_regular_file_raises_exception(self):
        output_path = os.path.join(self.dir.name, "not_a_directory")
        with open(output_path, "w") as file:
            file.write("")
        pixels = self.store.load(self.image_path)

        with self.assertRaises(Exception) as context:
            self.store.save(pixels, output_path, "saved", "png")

        output_file_path = os.path.join(output_path, "saved.png")
        self.assertIs(Exception, type(context.exception))
        self.assertTrue(
            str(context.exception).startswith(
                "An unexpected error occurred while saving image "
                f"{output_file_path}: "
            )
        )
