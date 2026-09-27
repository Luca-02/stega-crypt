import base64
from typing import Optional

from src.cryptography.aes_gcm import AesGcmCipher
from src.cryptography.password_handler import Password
from src.logger import logger


def decrypt_message(
    encrypted_data: bytes,
    password: Optional[str] = None,
) -> bytes:
    """Decrypt encrypted data with a password, delegating to AesGcmCipher.

    Temporary thin wrapper kept for backward compatibility while the
    surrounding code is migrated to the object-oriented design; it will
    be removed once callers use AesGcmCipher and Password directly.

    The base64 decoding happens before password validation, matching the
    current behavior: an invalid base64 input paired with an invalid
    password still surfaces the base64 error, not InvalidPasswordError.

    Args:
        encrypted_data: The encrypted message in base64 format
            (salt + nonce + ciphertext + tag).
        password: The raw password to derive the key from.

    Returns:
        The decrypted message.

    Raises:
        InvalidPasswordError: If the password is empty or invalid.
        DecryptionError: If the password is wrong or the data is
            corrupted.
    """
    logger.info("Decryption procedure begins")
    raw = base64.b64decode(encrypted_data)
    parsed_password = Password.parse(password)
    return AesGcmCipher().decrypt(raw, parsed_password)
