import os

from PIL import UnidentifiedImageError

from src.exceptions import (
    FileAlreadyExistsError,
    ImageFileNotFoundError,
    InputMessageConflictError,
    InvalidPasswordError,
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
                image_name=self.image_name,
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
            image_name=self.image_name,
        )

        with self.assertRaises(FileAlreadyExistsError):
            encode_message(
                image_path=self.image_path,
                message=self.message,
                output_path=self.output_path,
                image_name=self.image_name,
            )

    def test_encode_invalid_output_path_error(self):
        with self.assertRaises(Exception):
            encode_message(
                image_path=self.image_path,
                message=self.message,
                output_path="\x00",
            )

    def test_encode_input_message_conflict_error_text(self):
        with self.assertRaises(InputMessageConflictError) as context:
            encode_message(
                image_path="non_existent_image.png",
                message="test",
                message_path="non_existent_message.txt",
                output_path=self.output_path,
            )

        self.assertEqual(
            "Input message conflict, choose whether to use a string "
            "or a text file",
            str(context.exception),
        )

    def test_encode_empty_message_error_text(self):
        with self.assertRaises(NoMessageFoundError) as context:
            encode_message(
                image_path="non_existent_image.png",
                message="",
                output_path=self.output_path,
            )

        self.assertEqual(
            "You can't use an empty message.", str(context.exception)
        )

    def test_encode_empty_message_with_message_path_is_not_a_conflict(self):
        new_image_path = encode_message(
            image_path=self.image_path,
            message="",
            message_path=self.message_path,
            output_path=self.output_path,
            image_name=self.image_name,
        )

        self.assertEqual(self.encoded_image_path, new_image_path)

    def test_encode_message_file_not_found_error_text(self):
        message_path = "non_existent_message.txt"

        with self.assertRaises(MessageFileNotFoundError) as context:
            encode_message(
                image_path=self.image_path,
                message_path=message_path,
                output_path=self.output_path,
            )

        self.assertEqual(
            f'The file "{message_path}" was not found, '
            "please verify the path.",
            str(context.exception),
        )

    def test_encode_image_file_not_found_error_text(self):
        image_path = "non_existent_image.png"

        with self.assertRaises(ImageFileNotFoundError) as context:
            encode_message(
                image_path=image_path,
                message=self.message,
                output_path=self.output_path,
            )

        self.assertEqual(
            f'The file "{image_path}" was not found, please verify the path.',
            str(context.exception),
        )

    def test_encode_unidentified_image_error_text(self):
        invalid_image_path = os.path.join(self.dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError) as context:
            encode_message(
                image_path=invalid_image_path,
                message=self.message,
                output_path=self.output_path,
            )

        self.assertEqual(
            f'The file "{invalid_image_path}" is not a valid image '
            "or is corrupt.",
            str(context.exception),
        )

    def test_encode_output_file_already_exists_error_text(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
        )

        with self.assertRaises(FileAlreadyExistsError) as context:
            encode_message(
                image_path=self.image_path,
                message=self.message,
                output_path=self.output_path,
                image_name=self.image_name,
            )

        self.assertEqual(
            f'The file "{self.encoded_image_path}" already exists '
            f'in the directory "{self.output_path}".',
            str(context.exception),
        )

    def test_encode_image_is_loaded_before_password_validation(self):
        with self.assertRaises(ImageFileNotFoundError):
            encode_message(
                image_path="non_existent_image.png",
                message=self.message,
                output_path=self.output_path,
                password="   ",
            )

    def test_encode_password_is_validated_before_capacity_check(self):
        with self.assertRaises(InvalidPasswordError):
            encode_message(
                image_path=self.image_path,
                message="A" * (self.img_size[0] ** 2 * 2),
                output_path=self.output_path,
                password="   ",
                compress=False,
            )

    def test_encode_capacity_is_checked_before_output_file_exists(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
        )

        with self.assertRaises(MessageTooLargeError):
            encode_message(
                image_path=self.image_path,
                message="A" * (self.img_size[0] ** 2 * 2),
                output_path=self.output_path,
                image_name=self.image_name,
                compress=False,
            )
