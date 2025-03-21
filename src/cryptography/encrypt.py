import base64

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from .derivation import derive_key_from_password
from .password_handler import clean_password


def encrypt_data(data: bytes, password: str) -> bytes:
    """
    Encrypt data with a password or key from file.

    :param data: The data to encrypt.
    :param password: The password to derive the key.
    :return: The encrypted data in base64 format.
    :raises ValueError: If the password is empty
    """
    password = clean_password(password)
    if password:
        salt = get_random_bytes(16)
        key = derive_key_from_password(password, salt)
    else:
        raise ValueError('You must provide a password.')

    # Creating the AES-GCM cipher
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    # 16 byte + 16 bytes + msg bytes + 16 bytes
    encrypted_data = salt + cipher.nonce + ciphertext + tag

    return base64.b64encode(encrypted_data)
