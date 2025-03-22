import base64
from typing import Optional

from Crypto.Cipher import AES

from ..config import NONCE_SIZE_BYTE, SALT_SIZE_BYTE, TAG_SIZE_BYTE
from ..exceptions import DecryptionError, InvalidPasswordError
from .derivation import derive_key_from_password
from .password_handler import clean_password, is_valid_password


def decrypt_message(encrypted_data: bytes, password: Optional[str] = None) -> bytes:
    """
    Decrypts encrypted data using a password or key from a file.

    :param encrypted_data: The encrypted message in base64 format (salt + nonce + ciphertext + tag).
    :param password: The password to derive the key (optional).
    :return: The decrypted message.
    :raises InvalidPasswordError: If the password is empty or decryption fails.
    """
    password = clean_password(password)
    encrypted_data = base64.b64decode(encrypted_data)

    # Salt is the first 16 bytes
    salt = encrypted_data[:SALT_SIZE_BYTE]
    # Nonce is the next 16 bytes
    nonce = encrypted_data[SALT_SIZE_BYTE : SALT_SIZE_BYTE + NONCE_SIZE_BYTE]
    # Ciphertext is everything in between
    ciphertext = encrypted_data[SALT_SIZE_BYTE + NONCE_SIZE_BYTE : -TAG_SIZE_BYTE]
    # Tag is the last 16 bytes
    tag = encrypted_data[-TAG_SIZE_BYTE:]

    if is_valid_password(password):
        key = derive_key_from_password(password, salt)
    else:
        raise InvalidPasswordError("You must provide a password.")

    # Creating the AES-GCM cipher
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Decrypt and verify integrity
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        raise DecryptionError("Decryption error: incorrect key or corrupted data.")
