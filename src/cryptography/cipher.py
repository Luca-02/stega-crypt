from typing import Protocol

from src.cryptography.password_handler import Password


class Cipher(Protocol):
    """Common interface for symmetric encryption algorithms.

    Implementations work on raw bytes: no base64 encoding or decoding
    happens here. That concern belongs to the payload layer, not to the
    cipher itself.
    """

    def encrypt(self, data: bytes, password: Password) -> bytes:
        """Encrypt raw bytes with a password.

        Args:
            data: The plaintext bytes to encrypt.
            password: An already validated password.

        Returns:
            The encrypted bytes, in whatever format the implementation
            defines. No base64 encoding is applied.
        """
        ...

    def decrypt(self, data: bytes, password: Password) -> bytes:
        """Decrypt bytes previously produced by ``encrypt``.

        Args:
            data: The encrypted bytes to decrypt. No base64 decoding is
                applied before this call.
            password: An already validated password.

        Returns:
            The decrypted plaintext bytes.

        Raises:
            DecryptionError: If the password is wrong or the data is
                corrupted.
        """
        ...
