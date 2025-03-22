import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from PIL import Image, UnidentifiedImageError

from src.exceptions import (
    FileAlreadyExistsError,
    ImageFileNotFoundError,
    MessageFileNotFoundError,
    MessageTooLargeError,
    NoMessageFoundError,
)
from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message


class Test(TestCase):
    def setUp(self) -> None:
        self.dir = TemporaryDirectory()
        self.message_path = os.path.join(self.dir.name, "message.txt")
        self.image_path = os.path.join(self.dir.name, "img.png")
        self.output_path = os.path.join(self.dir.name, "test_output_dir")
        self.message = "Hello World!"
        self.password = "password123"
        self.img_size = (100, 100)

        with open(self.message_path, "w") as file:
            file.write(self.message)

        img = Image.new("RGB", self.img_size, color=(10, 20, 30))
        img.save(self.image_path, "png")

    def tearDown(self) -> None:
        self.dir.cleanup()

    def test_steganography(self):
        encoded_image_path = os.path.join(self.output_path, "encoded_image.png")

        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            new_image_name="encoded_image",
            compress=False,
        )
        decoded_message = decode_message(encoded_image_path)

        self.assertTrue(os.path.isfile(encoded_image_path))
        self.assertEqual(self.message, decoded_message)

    def test_steganography_compression(self):
        encoded_image_path = os.path.join(self.output_path, "encoded_image.png")

        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            new_image_name="encoded_image",
            compress=True,
        )
        decoded_message = decode_message(encoded_image_path)

        self.assertTrue(os.path.isfile(encoded_image_path))
        self.assertEqual(self.message, decoded_message)

    def test_steganography_message_from_file(self):
        encoded_image_path = os.path.join(self.output_path, "encoded_image.png")

        encode_message(
            image_path=self.image_path,
            message_path=self.message_path,
            output_path=self.output_path,
            new_image_name="encoded_image",
            compress=False,
        )
        decoded_message = decode_message(encoded_image_path)

        self.assertTrue(os.path.isfile(encoded_image_path))
        self.assertEqual(self.message, decoded_message)

    def test_steganography_encryption(self):
        encoded_image_path = os.path.join(self.output_path, "encoded_image.png")

        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            new_image_name="encoded_image",
            password=self.password,
            compress=True,
        )
        decoded_message = decode_message(encoded_image_path, password=self.password)

        self.assertTrue(os.path.isfile(encoded_image_path))
        self.assertEqual(self.message, decoded_message)

    def test_encode_empty_message_error(self):
        with self.assertRaises(NoMessageFoundError):
            encode_message(
                image_path=self.image_path, message="", output_path=self.output_path
            )

    def test_encode_message_too_large_error(self):
        with self.assertRaises(MessageTooLargeError):
            encode_message(
                image_path=self.image_path,
                message="A" * (self.img_size[0] ** 2 * 2),
                output_path=self.output_path,
                new_image_name="encoded_image",
                password=self.password,
                compress=True,
            )

    def test_encode_message_file_not_found_error(self):
        with self.assertRaises(MessageFileNotFoundError):
            encode_message(
                image_path=self.image_path,
                message_path="non_existent_message.txt",
                output_path=self.output_path,
            )

    def test_encode_invalid_message_path_error(self):
        with self.assertRaises(Exception):
            encode_message(
                image_path=self.image_path,
                message_path="\x00",
                output_path=self.output_path,
            )

    def test_encode_image_file_not_found_error(self):
        with self.assertRaises(ImageFileNotFoundError):
            encode_message(
                image_path="non_existent_image.png",
                message_path=self.message_path,
                output_path=self.output_path,
            )

    def test_encode_unidentified_image_error(self):
        invalid_image_path = os.path.join(self.dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError):
            encode_message(
                image_path=invalid_image_path,
                message=self.message,
                output_path=self.output_path,
            )

    def test_encode_invalid_image_file_path_error(self):
        with self.assertRaises(Exception):
            encode_message(
                image_path="\x00",
                message=self.message,
                output_path=self.output_path,
            )

    def test_encode_output_file_already_exists_error(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            new_image_name="encoded_image",
        )

        with self.assertRaises(FileAlreadyExistsError):
            encode_message(
                image_path=self.image_path,
                message=self.message,
                output_path=self.output_path,
                new_image_name="encoded_image",
            )

    def test_encode_invalid_output_path_error(self):
        with self.assertRaises(Exception):
            encode_message(
                image_path=self.image_path,
                message=self.message,
                output_path="\x00",
            )

    def test_decode_empty_image_error(self):
        invalid_image_path = os.path.join(self.dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError):
            decode_message(invalid_image_path)
