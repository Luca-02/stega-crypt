from unittest import TestCase
from unittest.mock import mock_open, patch

from src.steganography.file_handler import load_message_file


class TestFileHandler(TestCase):
    def test_load_message_file_uses_locale_encoding(self):
        # Known asymmetry kept by the refactor: messages are read with the
        # platform default encoding but saved as UTF-8.
        with patch(
            "src.steganography.file_handler.open",
            mock_open(read_data="message"),
            create=True,
        ) as mocked_open:
            message = load_message_file("message.txt")

        mocked_open.assert_called_once_with("message.txt", "r")
        self.assertEqual("message", message)
