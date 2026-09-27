import os
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import mock_open, patch

from src.exceptions import FileAlreadyExistsError
from src.steganography.file_handler import (
    ensure_directory_exists,
    ensure_file_does_not_exist,
    load_message_file,
)


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


class TestEnsureFileDoesNotExist(TestCase):
    def setUp(self) -> None:
        self.dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.dir.cleanup()

    def test_does_nothing_when_directory_does_not_exist(self):
        output_path = os.path.join(self.dir.name, "missing_dir")
        file_name = os.path.join(output_path, "file.txt")

        ensure_file_does_not_exist(output_path, file_name)

    def test_does_nothing_when_file_does_not_exist(self):
        file_name = os.path.join(self.dir.name, "file.txt")

        ensure_file_does_not_exist(self.dir.name, file_name)

    def test_raises_when_directory_and_file_exist(self):
        file_name = os.path.join(self.dir.name, "file.txt")
        with open(file_name, "w") as file:
            file.write("")

        with self.assertRaises(FileAlreadyExistsError) as context:
            ensure_file_does_not_exist(self.dir.name, file_name)

        self.assertEqual(
            f'The file "{file_name}" already exists '
            f'in the directory "{self.dir.name}".',
            str(context.exception),
        )


class TestEnsureDirectoryExists(TestCase):
    def setUp(self) -> None:
        self.dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.dir.cleanup()

    def test_creates_nested_directories(self):
        nested_dir = os.path.join(self.dir.name, "a", "b", "c")

        ensure_directory_exists(nested_dir)

        self.assertTrue(os.path.isdir(nested_dir))

    def test_does_nothing_when_directory_already_exists(self):
        ensure_directory_exists(self.dir.name)

        self.assertTrue(os.path.isdir(self.dir.name))
