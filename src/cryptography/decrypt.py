import base64
from typing import Optional

from Crypto.Cipher import AES

from .derivation import derive_key_from_password
from .password_handler import clean_password
from ..exceptions import InvalidPasswordError, DecryptionError


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

    # Extract salt, nonce, ciphertext, and tag
    salt = encrypted_data[:16]  # Salt is the first 16 bytes
    nonce = encrypted_data[16:32]  # Nonce is the next 16 bytes
    ciphertext = encrypted_data[32:-16]  # Ciphertext is everything in between
    tag = encrypted_data[-16:]  # Tag is the last 16 bytes

    if password:
        key = derive_key_from_password(password, salt)
    else:
        raise InvalidPasswordError('You must provide a password.')

    # Creating the AES-GCM cipher
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Decrypt and verify integrity
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        raise DecryptionError("Decryption error: incorrect key or corrupted data.")
