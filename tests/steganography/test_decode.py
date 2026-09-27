import os

from PIL import UnidentifiedImageError

from src.exceptions import DecryptionError, FileAlreadyExistsError
from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message
from tests.steganography.base_test_stenography import BaseTestSteganography


class Test(BaseTestSteganography):
    def test_decode_invalid_image(self):
        invalid_image_path = os.path.join(self.dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError):
            decode_message(invalid_image_path)

    def test_decode_output_file_already_exists_error(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
            password=self.password,
            compress=True,
        )
        decode_message(
            self.encoded_image_path,
            output_path=self.output_path,
            save_message=True,
            password=self.password,
        )

        with self.assertRaises(FileAlreadyExistsError):
            decode_message(
                self.encoded_image_path,
                output_path=self.output_path,
                save_message=True,
                password=self.password,
            )

    def test_decode_invalid_output_path_error(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
            password=self.password,
            compress=True,
        )

        with self.assertRaises(Exception):
            decode_message(
                self.encoded_image_path,
                output_path="\x00",
                message_name=self.message_name,
                save_message=True,
                password=self.password,
            )

    def test_decode_wrong_password_error_text(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
            password=self.password,
            compress=False,
        )

        with self.assertRaises(DecryptionError) as context:
            decode_message(self.encoded_image_path, password="wrong_password")

        self.assertEqual(
            "Decryption error: incorrect key or corrupted data.",
            str(context.exception),
        )

    def test_decode_output_file_already_exists_error_text(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
        )
        message_path = decode_message(
            self.encoded_image_path,
            output_path=self.output_path,
            message_name=self.message_name,
            save_message=True,
        )

        with self.assertRaises(FileAlreadyExistsError) as context:
            decode_message(
                self.encoded_image_path,
                output_path=self.output_path,
                message_name=self.message_name,
                save_message=True,
            )

        self.assertEqual(
            f'The file "{message_path}" already exists '
            f'in the directory "{self.output_path}".',
            str(context.exception),
        )

    def test_decode_save_message_error_text(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
        )
        not_a_directory = os.path.join(self.dir.name, "not_a_directory")
        with open(not_a_directory, "w") as file:
            file.write("")

        with self.assertRaises(Exception) as context:
            decode_message(
                self.encoded_image_path,
                output_path=not_a_directory,
                message_name="message",
                save_message=True,
            )

        output_file_path = os.path.join(not_a_directory, "message.txt")
        self.assertIs(Exception, type(context.exception))
        self.assertTrue(
            str(context.exception).startswith(
                "An unexpected error occurred while saving image "
                f"{output_file_path}: "
            )
        )
