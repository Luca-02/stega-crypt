import base64
from typing import Optional

from Crypto.Cipher import AES

from src.config import NONCE_SIZE_BYTE, SALT_SIZE_BYTE, TAG_SIZE_BYTE
from src.cryptography.derivation import derive_key_from_password
from src.cryptography.password_handler import clean_password, is_valid_password
from src.exceptions import DecryptionError, InvalidPasswordError
from src.logger import logger


def decrypt_message(
    encrypted_data: bytes,
    password: Optional[str] = None,
) -> bytes:
    """
    Decrypts encrypted data using a password or key from a file.

    :param encrypted_data: The encrypted message in base64 format (salt + nonce + ciphertext + tag).
    :param password: The password to derive the key (optional).
    :return: The decrypted message.
    :raises InvalidPasswordError: If the password is empty or decryption fails.
    """
    logger.info("Decryption procedure begins")

    password = clean_password(password)
    encrypted_data = base64.b64decode(encrypted_data)

    # Salt is the first 16 bytes
    salt = encrypted_data[:SALT_SIZE_BYTE]
    # Nonce is the next 16 bytes
    nonce = encrypted_data[SALT_SIZE_BYTE : SALT_SIZE_BYTE + NONCE_SIZE_BYTE]
    # Ciphertext is everything in between
    ciphertext_bottom = SALT_SIZE_BYTE + NONCE_SIZE_BYTE
    ciphertext_upper = -TAG_SIZE_BYTE
    ciphertext = encrypted_data[ciphertext_bottom:ciphertext_upper]
    # Tag is the last 16 bytes
    tag = encrypted_data[-TAG_SIZE_BYTE:]

    logger.debug(
        f"Decryption data: "
        f"salt={len(salt)} byte, "
        f"nonce={len(nonce)} byte, "
        f"ciphertext={len(ciphertext)} byte, "
        f"tag={len(tag)} byte"
    )

    if is_valid_password(password):
        logger.debug("Password validated, key derivation in progress")
        key = derive_key_from_password(password, salt)
    else:
        raise InvalidPasswordError("You must provide a password.")

    try:
        # Creating the AES-GCM cipher
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        # Decrypt and verify integrity
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        logger.info("Message decryption completed successfully")

        return decrypted_data
    except ValueError:
        raise DecryptionError(
            "Decryption error: incorrect key or corrupted data."
        )
