import base64

from Crypto.Cipher import AES

from src.config import SALT_SIZE_BYTE
from src.cryptography.derivation import derive_key_from_password, generate_salt
from src.cryptography.password_handler import clean_password, is_valid_password
from src.exceptions import InvalidPasswordError
from src.logger import logger


def encrypt_data(data: bytes, password: str) -> bytes:
    """
    Encrypt data with a password or key from file.

    :param data: The data to encrypt.
    :param password: The password to derive the key.
    :return: The encrypted data in base64 format.
    :raises InvalidPasswordError: If the password is empty
    """
    logger.info("Starting data encryption")

    password = clean_password(password)

    if is_valid_password(password):
        logger.debug("Password validation successful")
        salt = generate_salt(SALT_SIZE_BYTE)
        key = derive_key_from_password(password, salt)
    else:
        raise InvalidPasswordError("You must provide a password.")

    # Creating the AES-GCM cipher
    logger.debug("AES-GCM Cipher Creation")
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    # 16 byte + 16 bytes + msg bytes + 16 bytes
    encrypted_data = salt + cipher.nonce + ciphertext + tag

    logger.info(f"Encryption completed: data={len(encrypted_data)} bytes")
    return base64.b64encode(encrypted_data)
