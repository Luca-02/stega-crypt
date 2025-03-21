import hashlib
import os

from ..config import KEY_DERIVATION_ITERATIONS, AES_KEY_LENGTH_BYTE


def generate_salt(byte_size: int) -> bytes:
    """
    Generate a random salt for use in key derivation.

    :return: A random salt as bytes.
    """
    return os.urandom(byte_size)


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Generates a secure 32 byte key from a password using PBKDF2.

    :param password: The user provided password.
    :param salt: A random salt to make the key derivation more secure.
    :return: A 32 byte key for AES encryption.
    """
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        KEY_DERIVATION_ITERATIONS,
        dklen=AES_KEY_LENGTH_BYTE
    )
