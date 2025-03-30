from unittest import TestCase

from src.cryptography.decrypt import decrypt_message
from src.cryptography.encrypt import encrypt_data
from src.exceptions import DecryptionError, InvalidPasswordError


class Test(TestCase):
    def setUp(self) -> None:
        self.message = "Secrete message".encode()
        self.password = "password123"

    def test_cryptography(self):
        encrypted = encrypt_data(self.message, password=self.password)
        decrypted = decrypt_message(encrypted, password=self.password)

        self.assertEqual(self.message, decrypted)

    def test_encrypt_empty_password(self):
        with self.assertRaises(InvalidPasswordError):
            encrypt_data(self.message, password="")

    def test_encrypt_invalid_password(self):
        with self.assertRaises(InvalidPasswordError):
            encrypt_data(self.message, password="c1A 0!?")

    def test_dencrypt_empty_password(self):
        with self.assertRaises(InvalidPasswordError):
            encrypted = encrypt_data(self.message, password=self.password)
            decrypt_message(encrypted, password="")

    def test_dencrypt_invalid_password(self):
        with self.assertRaises(InvalidPasswordError):
            encrypted = encrypt_data(self.message, password=self.password)
            decrypt_message(encrypted, password="c1A 0!?")

    def test_dencrypt_wrong_password(self):
        with self.assertRaises(DecryptionError):
            encrypted = encrypt_data(self.message, password=self.password)
            decrypt_message(encrypted, password="wrong_password")
