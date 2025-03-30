import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from PIL import Image


class BaseTestSteganography(TestCase):
    def setUp(self) -> None:
        self.dir = TemporaryDirectory()
        self.message_path = os.path.join(self.dir.name, "message.txt")
        self.image_path = os.path.join(self.dir.name, "img.png")
        self.output_path = os.path.join(self.dir.name, "test_output_dir")
        self.image_name = os.path.join(self.output_path, "encoded_image")
        self.encoded_image_path = os.path.join(
            self.output_path, f"{self.image_name}.png"
        )
        self.message_name = os.path.join(self.output_path, "decoded_message")
        self.message = "Hello World!"
        self.long_message = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
        commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
        velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
        cupidatat non proident, sunt in culpa qui officia deserunt mollit anim
        id est laborum.
        """
        self.password = "password123"
        self.img_size = (100, 100)

        with open(self.message_path, "w") as file:
            file.write(self.message)

        img = Image.new("RGB", self.img_size, color=(10, 20, 30))
        img.save(self.image_path, "png")

    def tearDown(self) -> None:
        self.dir.cleanup()
