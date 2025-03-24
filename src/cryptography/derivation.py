import hashlib
import os

from src.config import (
    AES_KEY_LENGTH_BYTE,
    KEY_DERIVATION_HASH,
    KEY_DERIVATION_ITERATIONS,
)


def generate_salt(byte_size: int) -> bytes:
    """
    Generate a random salt for use in key derivation.

    :return: A random salt as bytes.
    """
    return os.urandom(byte_size)


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Generates a secure AES_KEY_LENGTH_BYTE byte key from a password using PBKDF2.

    :param password: The user provided password.
    :param salt: A salt to make key derivation more secure.
    :return: An AES_KEY_LENGTH_BYTE byte key for AES encryption.
    """
    return hashlib.pbkdf2_hmac(
        KEY_DERIVATION_HASH,
        password.encode(),
        salt,
        KEY_DERIVATION_ITERATIONS,
        dklen=AES_KEY_LENGTH_BYTE,
    )
