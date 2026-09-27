import os

from PIL import Image

from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message
from src.steganography.file_handler import load_message_file
from tests.steganography import reference
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
            output_path=self.output_path,
            message_name=self.message_name,
            save_message=True,
            password=self.password,
        )
        message = load_message_file(decoded_message_path)

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

        decoded_message = decode_message(image_path=self.encoded_image_path)

        self.assertTrue(os.path.isfile(self.encoded_image_path))
        self.assertNotEqual(self.message, decoded_message)
        self.assertEqual(
            self.message.encode(),
            reference.decrypt(decoded_message.encode(), self.password),
        )

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
            image_path=self.encoded_image_path,
            message_name=None,
            password=self.password,
        )

        self.assertTrue(os.path.isfile(self.encoded_image_path))
        self.assertEqual(self.message, decoded_message)

    def test_default_image_name(self):
        new_image_path = encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
        )

        expected = os.path.join(self.output_path, "img-modified.png")
        self.assertEqual(expected, new_image_path)
        self.assertTrue(os.path.isfile(expected))

    def test_default_message_name(self):
        new_image_path = encode_message(
            image_path=self.image_path,
            message=self.message,
            output_path=self.output_path,
        )

        message_path = decode_message(
            new_image_path,
            output_path=self.output_path,
            save_message=True,
        )

        expected = os.path.join(self.output_path, "img-modified-message.txt")
        self.assertEqual(expected, message_path)
        with open(expected, "rb") as file:
            self.assertEqual(self.message.encode("utf-8"), file.read())

    def test_saved_message_is_utf8(self):
        message = "Caffè ✓"
        encode_message(
            image_path=self.image_path,
            message=message,
            output_path=self.output_path,
            image_name=self.image_name,
        )

        message_path = decode_message(
            self.encoded_image_path,
            output_path=self.output_path,
            message_name=self.message_name,
            save_message=True,
        )

        with open(message_path, "rb") as file:
            self.assertEqual(message.encode("utf-8"), file.read())

    def test_output_format_follows_input_extension(self):
        bmp_path = os.path.join(self.dir.name, "img.bmp")
        Image.new("RGB", self.img_size, color=(10, 20, 30)).save(bmp_path)

        new_image_path = encode_message(
            image_path=bmp_path,
            message=self.message,
            output_path=self.output_path,
        )

        self.assertEqual(
            os.path.join(self.output_path, "img-modified.bmp"), new_image_path
        )
        with Image.open(new_image_path) as img:
            self.assertEqual("BMP", img.format)
        self.assertEqual(self.message, decode_message(new_image_path))

    def test_jpg_extension_cannot_be_saved(self):
        jpg_path = os.path.join(self.dir.name, "img.jpg")
        Image.new("RGB", self.img_size, color=(10, 20, 30)).save(
            jpg_path, "jpeg"
        )

        with self.assertRaises(Exception) as context:
            encode_message(
                image_path=jpg_path,
                message=self.message,
                output_path=self.output_path,
            )

        output_file_path = os.path.join(self.output_path, "img-modified.jpg")
        self.assertIs(Exception, type(context.exception))
        self.assertTrue(
            str(context.exception).startswith(
                "An unexpected error occurred while saving image "
                f"{output_file_path}: "
            )
        )

    def test_steganography_image_modes(self):
        for mode, color in (("L", 10), ("RGBA", (10, 20, 30, 40))):
            with self.subTest(mode=mode):
                image_path = os.path.join(self.dir.name, f"img-{mode}.png")
                Image.new(mode, self.img_size, color=color).save(image_path)

                new_image_path = encode_message(
                    image_path=image_path,
                    message=self.message,
                    output_path=self.output_path,
                )

                with Image.open(new_image_path) as img:
                    self.assertEqual(mode, img.mode)
                self.assertEqual(
                    reference.load_pixels(image_path).shape,
                    reference.load_pixels(new_image_path).shape,
                )
                self.assertEqual(self.message, decode_message(new_image_path))
