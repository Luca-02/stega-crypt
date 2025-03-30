from unittest import TestCase

from src.cryptography.password_handler import is_valid_password


class Test(TestCase):
    def test_valid_password(self):
        password = "c1A0!?"
        self.assertTrue(is_valid_password(password))

    def test_invalid_password_character(self):
        password = "c1A 0!?"
        self.assertFalse(is_valid_password(password))

    def test_invalid_password_length(self):
        password = "c1A"
        self.assertFalse(is_valid_password(password))
