import os

from PIL import UnidentifiedImageError

from src.exceptions import (
    FileAlreadyExistsError,
    ImageFileNotFoundError,
    InputMessageConflictError,
    MessageFileNotFoundError,
    MessageTooLargeError,
    NoMessageFoundError,
)
from src.steganography.encoder import encode_message
from tests.steganography.base_test_stenography import BaseTestSteganography


class Test(BaseTestSteganography):
    def test_encode_input_message_conflict_error(self):
        with self.assertRaises(InputMessageConflictError):
            encode_message(
                image_path=self.image_path,
                message="test",
                message_path="test",
                output_path=self.output_path,
            )

    def test_encode_empty_message_error(self):
        with self.assertRaises(NoMessageFoundError):
            encode_message(
                image_path=self.image_path,
                message="",
                output_path=self.output_path,
            )

    def test_encode_message_too_large_error(self):
        with self.assertRaises(MessageTooLargeError):
            encode_message(
                image_path=self.image_path,
                message="A" * (self.img_size[0] ** 2 * 2),
                output_path=self.output_path,
                image_name="encoded_image",
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
            image_name="encoded_image",
        )

        with self.assertRaises(FileAlreadyExistsError):
            encode_message(
                image_path=self.image_path,
                message=self.message,
                output_path=self.output_path,
                image_name="encoded_image",
            )

    def test_encode_invalid_output_path_error(self):
        with self.assertRaises(Exception):
            encode_message(
                image_path=self.image_path,
                message=self.message,
                output_path="\x00",
            )
