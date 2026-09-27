import base64
from unittest import TestCase

from src.cryptography.aes_gcm import AesGcmCipher, AesGcmEnvelope
from src.cryptography.cipher import Cipher
from src.cryptography.password_handler import Password
from src.exceptions import DecryptionError
from tests.steganography import reference

ENVELOPE_OVERHEAD = 48


class TestAesGcmCipher(TestCase):
    def setUp(self) -> None:
        self.cipher: Cipher = AesGcmCipher()
        self.password = Password.parse("password123")
        self.data = b"Secret message"

    def test_roundtrip(self):
        encrypted = self.cipher.encrypt(self.data, self.password)
        decrypted = self.cipher.decrypt(encrypted, self.password)

        self.assertEqual(self.data, decrypted)

    def test_output_length(self):
        encrypted = self.cipher.encrypt(self.data, self.password)

        self.assertEqual(len(encrypted), ENVELOPE_OVERHEAD + len(self.data))

    def test_two_encryptions_of_same_data_differ(self):
        first = self.cipher.encrypt(self.data, self.password)
        second = self.cipher.encrypt(self.data, self.password)

        self.assertNotEqual(first, second)

    def test_decrypt_envelope_built_independently(self):
        salt = bytes(range(16))
        nonce = bytes(range(16, 32))
        envelope = base64.b64decode(
            reference.encrypt(
                self.data, self.password.value, salt=salt, nonce=nonce
            )
        )

        decrypted = self.cipher.decrypt(envelope, self.password)

        self.assertEqual(self.data, decrypted)

    def test_encrypt_output_openable_by_reference(self):
        encrypted = self.cipher.encrypt(self.data, self.password)

        decrypted = reference.decrypt(
            base64.b64encode(encrypted), self.password.value
        )

        self.assertEqual(self.data, decrypted)

    def test_decrypt_wrong_password_raises_decryption_error(self):
        encrypted = self.cipher.encrypt(self.data, self.password)
        wrong_password = Password.parse("wrong_password")

        with self.assertRaises(DecryptionError) as ctx:
            self.cipher.decrypt(encrypted, wrong_password)

        self.assertEqual(
            str(ctx.exception),
            "Decryption error: incorrect key or corrupted data.",
        )

    def test_decrypt_truncated_blob_raises_decryption_error(self):
        truncated = bytes(20)

        with self.assertRaises(DecryptionError):
            self.cipher.decrypt(truncated, self.password)


class TestAesGcmEnvelope(TestCase):
    def test_to_bytes_roundtrip(self):
        envelope = AesGcmEnvelope(
            salt=bytes(range(16)),
            nonce=bytes(range(16, 32)),
            ciphertext=b"ciphertext-bytes",
            tag=bytes(range(32, 48)),
        )

        rebuilt = AesGcmEnvelope.from_bytes(envelope.to_bytes())

        self.assertEqual(envelope, rebuilt)

    def test_from_bytes_slices_known_blob(self):
        salt = bytes(range(16))
        nonce = bytes(range(16, 32))
        ciphertext = b"ciphertext-bytes"
        tag = bytes(range(32, 48))
        blob = salt + nonce + ciphertext + tag

        envelope = AesGcmEnvelope.from_bytes(blob)

        self.assertEqual(envelope.salt, salt)
        self.assertEqual(envelope.nonce, nonce)
        self.assertEqual(envelope.ciphertext, ciphertext)
        self.assertEqual(envelope.tag, tag)

    def test_from_bytes_does_not_raise_on_short_input(self):
        envelope = AesGcmEnvelope.from_bytes(bytes(20))

        self.assertIsInstance(envelope, AesGcmEnvelope)
