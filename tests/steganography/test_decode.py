import os

from PIL import UnidentifiedImageError

from src.steganography.decoder import decode_message
from tests.steganography.base_test_stenography import BaseTestSteganography


class Test(BaseTestSteganography):
    def test_decode_empty_image_error(self):
        invalid_image_path = os.path.join(self.dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError):
            decode_message(invalid_image_path)
