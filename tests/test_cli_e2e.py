"""End-to-end CLI tests on real images, without mocking the library."""

import os
from tempfile import TemporaryDirectory
from unittest import TestCase

import art
from click.testing import CliRunner, Result
from PIL import Image

from src.cli import cli
from src.config import ABOUT_PROJECT, PROJECT_NAME

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "fixtures", "cli"
)


class TestCliEndToEnd(TestCase):
    def setUp(self) -> None:
        self.dir = TemporaryDirectory()
        self.output_path = self.dir.name
        self.image_path = os.path.join(self.dir.name, "img.png")
        Image.new("RGB", (100, 100), color=(10, 20, 30)).save(self.image_path)
        self.message = "Secret message"
        self.password = "password123"
        self.runner = CliRunner()

    def tearDown(self) -> None:
        self.dir.cleanup()

    def invoke(self, args: list[str], user_input: str | None = None) -> Result:
        return self.runner.invoke(cli, args, input=user_input)

    def encode_encrypted(self) -> str:
        result = self.invoke(
            [
                "encode",
                self.image_path,
                "-m",
                self.message,
                "-op",
                self.output_path,
                "-in",
                "encoded",
                "-e",
            ],
            user_input=f"{self.password}\n{self.password}\n",
        )
        self.assertEqual(0, result.exit_code)
        return os.path.join(self.output_path, "encoded.png")

    def assert_help_snapshot(self, args: list[str], snapshot: str) -> None:
        result = self.runner.invoke(cli, args, terminal_width=80)
        with open(os.path.join(FIXTURES_DIR, snapshot)) as file:
            expected = file.read()

        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected, result.output)

    def test_help_output(self):
        self.assert_help_snapshot(["--help"], "cli_help.txt")
        self.assert_help_snapshot(["encode", "--help"], "encode_help.txt")
        self.assert_help_snapshot(["decode", "--help"], "decode_help.txt")

    def test_about_output(self):
        result = self.invoke(["about"])

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            art.text2art(PROJECT_NAME) + ABOUT_PROJECT + "\n", result.output
        )

    def test_plain_roundtrip_with_default_image_name(self):
        encoded_path = os.path.join(self.output_path, "img-modified.png")

        encode_result = self.invoke(
            [
                "encode",
                self.image_path,
                "-m",
                self.message,
                "-op",
                self.dir.name,
            ]
        )
        decode_result = self.invoke(["decode", encoded_path])

        self.assertEqual(0, encode_result.exit_code)
        self.assertEqual(
            f"Message embedded successfully into {encoded_path}\n",
            encode_result.output,
        )
        self.assertEqual(0, decode_result.exit_code)
        self.assertEqual(
            f"Message decoded successfully: \n{self.message}\n",
            decode_result.output,
        )

    def test_compressed_roundtrip_from_message_file(self):
        message_path = os.path.join(self.dir.name, "message.txt")
        long_message = "stega-crypt compressed message. " * 20
        with open(message_path, "w") as file:
            file.write(long_message)
        encoded_path = os.path.join(self.output_path, "encoded.png")

        encode_result = self.invoke(
            [
                "encode",
                self.image_path,
                "-mp",
                message_path,
                "-op",
                self.output_path,
                "-in",
                "encoded",
                "-c",
            ]
        )
        decode_result = self.invoke(["decode", encoded_path])

        self.assertEqual(0, encode_result.exit_code)
        self.assertEqual(
            f"Message embedded successfully into {encoded_path}\n",
            encode_result.output,
        )
        self.assertEqual(
            f"Message decoded successfully: \n{long_message}\n",
            decode_result.output,
        )

    def test_encrypted_roundtrip(self):
        encoded_path = os.path.join(self.output_path, "encoded.png")

        encode_result = self.invoke(
            [
                "encode",
                self.image_path,
                "-m",
                self.message,
                "-op",
                self.output_path,
                "-in",
                "encoded",
                "-e",
            ],
            user_input=f"{self.password}\n{self.password}\n",
        )
        decode_result = self.invoke(
            ["decode", encoded_path, "-d"], user_input=f"{self.password}\n"
        )

        self.assertEqual(0, encode_result.exit_code)
        self.assertEqual(
            "Password: \nConfirm password: \n"
            f"Message embedded successfully into {encoded_path}\n",
            encode_result.output,
        )
        self.assertEqual(0, decode_result.exit_code)
        self.assertEqual(
            f"Password: \nMessage decoded successfully: \n{self.message}\n",
            decode_result.output,
        )

    def test_decode_wrong_password(self):
        encoded_path = self.encode_encrypted()

        result = self.invoke(
            ["decode", encoded_path, "-d"], user_input="wrong_password\n"
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            "Password: \n"
            "Error: Decryption error: incorrect key or corrupted data.\n",
            result.output,
        )

    def test_save_message_without_name_prints_none(self):
        # Known bug kept by the refactor: the success message prints the
        # raw --message-name value, which is None when it is omitted.
        encoded_path = self.encode_encrypted()

        result = self.invoke(
            ["decode", encoded_path, "-d", "-sm", "-op", self.output_path],
            user_input=f"{self.password}\n",
        )

        saved_path = os.path.join(self.output_path, "encoded-message.txt")
        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            "Password: \n"
            f"Message saved successfully into {self.output_path}/None\n",
            result.output,
        )
        with open(saved_path, encoding="utf-8") as file:
            self.assertEqual(self.message, file.read())

    def test_save_message_with_name(self):
        encoded_path = self.encode_encrypted()

        result = self.invoke(
            [
                "decode",
                encoded_path,
                "-d",
                "-sm",
                "-op",
                self.output_path,
                "-mn",
                "secret",
            ],
            user_input=f"{self.password}\n",
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            "Password: \n"
            f"Message saved successfully into {self.output_path}/secret\n",
            result.output,
        )
        self.assertTrue(
            os.path.isfile(os.path.join(self.output_path, "secret.txt"))
        )

    def test_encode_error_exits_with_zero(self):
        missing_path = os.path.join(self.dir.name, "missing.png")

        result = self.invoke(
            ["encode", missing_path, "-m", self.message, "-op", self.dir.name]
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            f'Error: The file "{missing_path}" was not found, '
            "please verify the path.\n",
            result.output,
        )

    def test_password_prompt_abort_is_reported_as_error(self):
        result = self.invoke(
            [
                "encode",
                self.image_path,
                "-m",
                self.message,
                "-op",
                self.output_path,
                "-e",
            ],
            user_input="",
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual("Password: \n\nError: \n", result.output)
