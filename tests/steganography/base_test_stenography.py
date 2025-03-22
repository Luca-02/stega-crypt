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
        self.message = "Hello World!"
        self.password = "password123"
        self.img_size = (100, 100)

        with open(self.message_path, "w") as file:
            file.write(self.message)

        img = Image.new("RGB", self.img_size, color=(10, 20, 30))
        img.save(self.image_path, "png")

    def tearDown(self) -> None:
        self.dir.cleanup()
