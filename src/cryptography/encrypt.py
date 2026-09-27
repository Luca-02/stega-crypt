import base64

from src.cryptography.aes_gcm import AesGcmCipher
from src.cryptography.password_handler import Password
from src.logger import logger


def encrypt_data(data: bytes, password: str) -> bytes:
    """Encrypt data with a password, delegating to AesGcmCipher.

    Temporary thin wrapper kept for backward compatibility while the
    surrounding code is migrated to the object-oriented design; it will
    be removed once callers use AesGcmCipher and Password directly.

    Args:
        data: The data to encrypt.
        password: The raw password to derive the key from.

    Returns:
        The encrypted data in base64 format.

    Raises:
        InvalidPasswordError: If the password is empty or invalid.
    """
    logger.info("Starting data encryption")
    parsed_password = Password.parse(password)
    encrypted_data = AesGcmCipher().encrypt(data, parsed_password)
    return base64.b64encode(encrypted_data)
