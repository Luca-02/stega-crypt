from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from src.cli import cli, decode, encode
from src.config import DEFAULT_OUTPUT_DIR


class TestCli(TestCase):
    def setUp(self):
        self.img_format = "png"
        self.img_file = f"img.{self.img_format}"
        self.message_file = "message.txt"
        self.message = "Secret message"
        self.output_path = "./output"
        self.image_name = "new-img"
        self.message_name = "hidden-message"
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

    @patch("click.prompt")
    @patch("src.cli.encode_message")
    def test_encode_message(self, mock_encode_message, mock_prompt):
        mock_prompt.side_effect = [self.password, self.password]
        mock_encode_message.return_value = self.new_image_path

        runner = CliRunner()
        result = runner.invoke(
            encode,
            [
                self.img_file,
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
            image_path=self.img_file,
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
    def test_encode_message_from_file(self, mock_encode_message, mock_prompt):
        mock_prompt.side_effect = [self.password, self.password]
        mock_encode_message.return_value = self.new_image_path

        runner = CliRunner()
        result = runner.invoke(
            encode,
            [
                self.img_file,
                "--message-path",
                self.message_file,
                "--output-path",
                self.output_path,
                "--image-name",
                self.image_name,
                "--compress",
                "--encrypt",
            ],
        )

        mock_encode_message.assert_called_once_with(
            image_path=self.img_file,
            message=None,
            message_path=self.message_file,
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
        mock_prompt.side_effect = [self.password, "wrong_password"]
        mock_encode_message.return_value = self.new_image_path

        runner = CliRunner()
        result = runner.invoke(
            encode,
            [
                self.img_file,
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

    @patch("click.prompt")
    @patch("src.cli.decode_message")
    def test_decode_message(self, mock_decode_message, mock_prompt):
        mock_prompt.return_value = self.password
        mock_decode_message.return_value = self.message

        runner = CliRunner()
        result = runner.invoke(
            decode,
            [
                self.img_file,
                "--decrypt",
            ],
        )

        mock_decode_message.assert_called_once_with(
            image_path=self.img_file,
            output_path=DEFAULT_OUTPUT_DIR,
            message_name=None,
            password=self.password,
            save_message=False,
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            f"Message decoded successfully: \n{self.message}\n",
            result.output,
        )

    @patch("click.prompt")
    @patch("src.cli.decode_message")
    def test_decode_message_into_file(self, mock_decode_message, mock_prompt):
        mock_prompt.return_value = self.password
        mock_decode_message.return_value = self.message

        runner = CliRunner()
        result = runner.invoke(
            decode,
            [
                self.img_file,
                "--output-path",
                self.output_path,
                "--message-name",
                self.message_name,
                "--save-message",
                "--decrypt",
            ],
        )

        mock_decode_message.assert_called_once_with(
            image_path=self.img_file,
            output_path=self.output_path,
            message_name=self.message_name,
            password=self.password,
            save_message=True,
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            f"Message saved successfully into {self.output_path}/{self.message_name}\n",
            result.output,
        )

    @patch("click.prompt")
    @patch("src.cli.decode_message")
    def test_decode_exception(self, mock_decode_message, mock_prompt):
        error = "Decoding error"
        mock_prompt.return_value = self.password
        mock_decode_message.side_effect = Exception(error)

        runner = CliRunner()
        result = runner.invoke(
            decode,
            [
                self.img_file,
                "--decrypt",
            ],
        )

        mock_decode_message.assert_called_once_with(
            image_path=self.img_file,
            output_path=DEFAULT_OUTPUT_DIR,
            message_name=None,
            password=self.password,
            save_message=False,
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            f"Error: {error}\n",
            result.output,
        )
