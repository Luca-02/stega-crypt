import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from PIL import Image, UnidentifiedImageError

from src.steganography import encode, decode


class Test(TestCase):
    def setUp(self) -> None:
        self.test_dir = TemporaryDirectory()
        self.image_path = os.path.join(self.test_dir.name, "img.png")
        self.output_path = os.path.join(self.test_dir.name, "test_output_dir")
        self.img_size = (100, 100)

        img = Image.new('RGB', self.img_size, color=(255, 255, 255))
        img.save(self.image_path)

    def tearDown(self) -> None:
        self.test_dir.cleanup()

    def test_encode_decode_message(self):
        message = "Hello World!"
        encoded_image_path = os.path.join(self.output_path, "encoded_image.png")

        encode(self.image_path, message, output_path=self.output_path, new_image_name="encoded_image")
        decoded_message = decode(encoded_image_path)

        self.assertTrue(os.path.isfile(encoded_image_path))
        self.assertEqual(decoded_message, message)

    def test_empty_message(self):
        with self.assertRaises(ValueError):
            encode(self.image_path, "", output_path=self.output_path)

    def test_encode_large_message(self):
        width, height = self.img_size
        large_message = "A" * (width * height * 3 + 1)

        with self.assertRaises(ValueError):
            encode(self.image_path, large_message, output_path=self.output_path)

    def test_invalid_image_path(self):
        with self.assertRaises(FileNotFoundError):
            encode("non_existent_image.png", "Some message", output_path=self.output_path)

    def test_invalid_image_file(self):
        invalid_image_path = os.path.join(self.test_dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError):
            encode(invalid_image_path, "Some message", output_path=self.output_path)

    def test_file_exists_error(self):
        message = "Test message"
        encode(self.image_path, message, output_path=self.output_path, new_image_name="encoded_image")

        with self.assertRaises(FileExistsError):
            encode(self.image_path, message, output_path=self.output_path, new_image_name="encoded_image")

    def test_decode_empty_image(self):
        invalid_image_path = os.path.join(self.test_dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError):
            decode(invalid_image_path)
