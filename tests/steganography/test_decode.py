import os

from PIL import UnidentifiedImageError

from src.exceptions import FileAlreadyExistsError
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
