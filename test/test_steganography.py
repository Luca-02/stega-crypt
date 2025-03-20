import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from PIL import Image, UnidentifiedImageError

from src.decoder import decode_message
from src.encoder import encode_message


class Test(TestCase):
    def setUp(self) -> None:
        self.dir = TemporaryDirectory()
        self.message_path = os.path.join(self.dir.name, "message.txt")
        self.image_path = os.path.join(self.dir.name, "img.png")
        self.output_path = os.path.join(self.dir.name, "test_output_dir")
        self.img_size = (100, 100)

        img = Image.new("RGB", self.img_size, color=(10, 20, 30))
        img.save(self.image_path, "png")

    def tearDown(self) -> None:
        self.dir.cleanup()

    def test_encode_decode_message(self):
        message = "Hello World!"
        encoded_image_path = os.path.join(self.output_path, "encoded_image.png")

        encode_message(
            self.image_path,
            message,
            output_path=self.output_path,
            new_image_name="encoded_image",
            compress=False
        )
        decoded_message = decode_message(encoded_image_path)

        self.assertTrue(os.path.isfile(encoded_image_path))
        self.assertEqual(message, decoded_message)

    def test_encode_decode_message_compressed(self):
        message = "Hello World!"
        encoded_image_path = os.path.join(self.output_path, "encoded_image.png")

        encode_message(
            self.image_path,
            message=message,
            output_path=self.output_path,
            new_image_name="encoded_image",
            compress=True
        )
        decoded_message = decode_message(encoded_image_path)

        self.assertTrue(os.path.isfile(encoded_image_path))
        self.assertEqual(message, decoded_message)

    def test_encode_decode_message_from_file(self):
        message = "Hello World!"
        with open(self.message_path, 'w') as file:
            file.write(message)

        encoded_image_path = os.path.join(self.output_path, "encoded_image.png")

        encode_message(
            self.image_path,
            message_path=self.message_path,
            output_path=self.output_path,
            new_image_name="encoded_image",
            compress=False
        )
        decoded_message = decode_message(encoded_image_path)

        self.assertTrue(os.path.isfile(encoded_image_path))
        self.assertEqual(message, decoded_message)

    def test_empty_message(self):
        with self.assertRaises(ValueError):
            encode_message(self.image_path, "", output_path=self.output_path)

    def test_invalid_image_path(self):
        with self.assertRaises(FileNotFoundError):
            encode_message("non_existent_image.png", "Some message", output_path=self.output_path)

    def test_invalid_image_file(self):
        invalid_image_path = os.path.join(self.dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError):
            encode_message(invalid_image_path, "Some message", output_path=self.output_path)

    def test_file_exists_error(self):
        message = "Test message"
        encode_message(self.image_path, message, output_path=self.output_path, new_image_name="encoded_image")

        with self.assertRaises(FileExistsError):
            encode_message(self.image_path, message, output_path=self.output_path, new_image_name="encoded_image")

    def test_decode_empty_image(self):
        invalid_image_path = os.path.join(self.dir.name, "invalid_image.txt")
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image.")

        with self.assertRaises(UnidentifiedImageError):
            decode_message(invalid_image_path)
