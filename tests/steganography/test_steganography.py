import os

from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message
from tests.steganography.base_test_stenography import BaseTestSteganography


class Test(BaseTestSteganography):
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
