"""Test doubles shared by several test modules."""

from src.cryptography.password_handler import Password
from src.exceptions import DecryptionError


class FakeCipher:
    """Deterministic cipher that satisfies the Cipher protocol.

    Used to check that code depending on Cipher works with any
    implementation, not only with AES-GCM.
    """

    def encrypt(self, data: bytes, password: Password) -> bytes:
        """Prefix the data with a marker that includes the password.

        Args:
            data: The plaintext bytes.
            password: The validated password.

        Returns:
            The marked bytes.
        """
        return b"ENC:" + password.value.encode() + b":" + data

    def decrypt(self, data: bytes, password: Password) -> bytes:
        """Remove the marker added by ``encrypt``.

        Args:
            data: Bytes produced by ``encrypt``.
            password: The validated password.

        Returns:
            The original plaintext bytes.

        Raises:
            DecryptionError: If the marker does not match the password.
        """
        prefix = b"ENC:" + password.value.encode() + b":"
        if not data.startswith(prefix):
            raise DecryptionError("Fake decryption failed.")
        return data[len(prefix) :]
