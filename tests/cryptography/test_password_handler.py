import dataclasses
from unittest import TestCase

from src.cryptography.password_handler import Password, is_valid_password
from src.exceptions import InvalidPasswordError


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


class TestPassword(TestCase):
    def test_parse_strips_surrounding_whitespace(self):
        password = Password.parse("  abcd  ")
        self.assertEqual(password.value, "abcd")

    def test_parse_rejects_empty_password(self):
        with self.assertRaises(InvalidPasswordError) as ctx:
            Password.parse("")
        self.assertEqual(str(ctx.exception), "You must provide a password.")

    def test_parse_rejects_blank_password(self):
        with self.assertRaises(InvalidPasswordError) as ctx:
            Password.parse("   ")
        self.assertEqual(str(ctx.exception), "You must provide a password.")

    def test_parse_rejects_password_with_spaces(self):
        with self.assertRaises(InvalidPasswordError) as ctx:
            Password.parse("a b c d")
        self.assertEqual(str(ctx.exception), "You must provide a password.")

    def test_parse_rejects_password_too_short(self):
        with self.assertRaises(InvalidPasswordError) as ctx:
            Password.parse("abc")
        self.assertEqual(str(ctx.exception), "You must provide a password.")

    def test_repr_does_not_expose_value(self):
        password = Password.parse("secret123")
        self.assertNotIn("secret123", repr(password))

    def test_is_frozen(self):
        password = Password.parse("secret123")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            password.value = "other"

    def test_equality_by_value(self):
        first = Password.parse("secret123")
        second = Password.parse("secret123")
        self.assertEqual(first, second)
