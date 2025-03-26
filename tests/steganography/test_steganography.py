import os

from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message
from src.steganography.file_handler import load_message
from tests.steganography.base_test_stenography import BaseTestSteganography


class Test(BaseTestSteganography):
    def test_base_steganography(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
            compress=False,
        )
        decoded_message = decode_message(self.encoded_image_path)

        self.assertTrue(os.path.isfile(self.encoded_image_path))
        self.assertEqual(self.message, decoded_message)

    def test_steganography_with_compression(self):
        encode_message(
            image_path=self.image_path,
            message=self.long_message,
            output_path=self.output_path,
            image_name=self.image_name,
            compress=True,
        )
        decoded_message = decode_message(self.encoded_image_path)

        self.assertTrue(os.path.isfile(self.encoded_image_path))
        self.assertEqual(self.long_message, decoded_message)

    def test_steganography_with_encryption(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
            password=self.password,
            compress=True,
        )
        decoded_message = decode_message(
            self.encoded_image_path, password=self.password
        )

        self.assertTrue(os.path.isfile(self.encoded_image_path))
        self.assertEqual(self.message, decoded_message)

    def test_steganography_saving_message(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
            password=self.password,
            compress=True,
        )
        decoded_message_path = decode_message(
            self.encoded_image_path,
            save=True,
            output_path=self.output_path,
            message_name=self.message_name,
            password=self.password,
        )
        message = load_message(decoded_message_path)

        self.assertTrue(os.path.isfile(self.encoded_image_path))
        self.assertEqual(self.message, message)

    def test_steganography_with_missing_password(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
            password=self.password,
            compress=True,
        )

        decoded_message = decode_message(self.encoded_image_path)

        self.assertTrue(os.path.isfile(self.encoded_image_path))
        self.assertNotEqual(self.message, decoded_message)

    def test_steganography_encryption(self):
        encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
            image_name=self.image_name,
            password=self.password,
            compress=True,
        )
        decoded_message = decode_message(
            self.encoded_image_path, password=self.password
        )

        self.assertTrue(os.path.isfile(self.encoded_image_path))
        self.assertEqual(self.message, decoded_message)
