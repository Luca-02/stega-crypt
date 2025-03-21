import hashlib


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Generates a secure 32 byte key from a password using PBKDF2.

    :param password: The user provided password.
    :param salt: A random salt to make the key derivation more secure.
    :return: A 32 byte key for AES encryption.
    """
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000, dklen=32)
