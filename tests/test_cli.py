from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from src.cli import cli, encode
from src.config import ABOUT_PROJECT


class TestCli(TestCase):
    def setUp(self):
        self.img_format = "png"
        self.img = f"img.{self.img_format}"
        self.message = "Secret message"
        self.output_path = "./output"
        self.image_name = "new-img"
        self.new_image_path = (
            f"{self.output_path}/{self.image_name}.{self.img_format}"
        )
        self.password = "password123"

    @patch("src.cli.setup_logger")
    def test_cli_about(self, mock_setup_logger):
        runner = CliRunner()
        verbosity = "v" * 2
        result = runner.invoke(cli, [f"-{verbosity}", "about"])

        mock_setup_logger.assert_called_once_with(len(verbosity))

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(f"{ABOUT_PROJECT}\n", result.output)

    @patch("click.prompt")
    @patch("src.cli.encode_message")
    def test_encode(self, mock_encode_message, mock_prompt):
        mock_encode_message.return_value = self.new_image_path
        mock_prompt.side_effect = [self.password, self.password]

        runner = CliRunner()
        result = runner.invoke(
            encode,
            [
                self.img,
                "--message",
                self.message,
                "--output-path",
                self.output_path,
                "--image-name",
                self.image_name,
                "--compress",
                "--encrypt",
            ],
        )

        mock_encode_message.assert_called_once_with(
            image_path=self.img,
            message=self.message,
            message_path=None,
            output_path=self.output_path,
            image_name=self.image_name,
            compress=True,
            password=self.password,
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            f"Message embedded successfully into {self.new_image_path}\n",
            result.output,
        )

    @patch("click.prompt")
    @patch("src.cli.encode_message")
    def test_encode_incorrect_password(self, mock_encode_message, mock_prompt):
        mock_encode_message.return_value = self.new_image_path
        mock_prompt.side_effect = [self.password, "wrong_password"]

        runner = CliRunner()
        result = runner.invoke(
            encode,
            [
                self.img,
                "--message",
                self.message,
                "--output-path",
                self.output_path,
                "--image-name",
                self.image_name,
                "--compress",
                "--encrypt",
            ],
        )

        mock_encode_message.assert_not_called()

        self.assertEqual(0, result.exit_code)
        self.assertIn("Error: Passwords don't match!", result.output)
