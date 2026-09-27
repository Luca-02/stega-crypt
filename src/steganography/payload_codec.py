import base64

from src.config import DELIMITER_SUFFIX
from src.cryptography.cipher import Cipher
from src.cryptography.password_handler import Password
from src.logger import logger
from src.steganography.compressor import compress_message, decompress_message


class PayloadCodec:
    """Encodes and decodes the payload hidden inside an image.

    This is the only place that knows the on-disk format of the hidden
    payload: optional encryption with base64 encoding, optional
    compression with its own prefix, and the trailing delimiter. It
    depends on the Cipher protocol rather than on a specific
    implementation, so a different cipher can be plugged in without
    changing this class.
    """

    def __init__(self, cipher: Cipher) -> None:
        """Initialize the codec with a cipher implementation.

        Args:
            cipher: The cipher used to encrypt and decrypt the payload.
        """
        self._cipher = cipher

    def encode(
        self,
        message: str,
        password: str | None,
        compress: bool | None,
    ) -> bytes:
        """Build the payload to hide in the image.

        Args:
            message: The plaintext message to hide.
            password: If truthy, the message is encrypted with a key
                derived from this password. An empty string or None
                disables encryption.
            compress: If False, the data is stored as is. Otherwise it is
                compressed, but only when that makes it smaller.

        Returns:
            The encoded payload, ready to be embedded in the image.

        Raises:
            InvalidPasswordError: If a password is provided but is not
                valid.
        """
        logger.debug(
            f"Creating hidden message: "
            f"compression={compress}, password_provided={bool(password)}"
        )
        data = message.encode()

        if password:
            logger.debug("Encrypting message")
            logger.info("Starting data encryption")
            parsed_password = Password.parse(password)
            encrypted = self._cipher.encrypt(data, parsed_password)
            data = base64.b64encode(encrypted)

        if compress is False:
            hidden_message = data
            logger.debug("No compression applied")
        else:
            hidden_message = compress_message(data)
            logger.debug("Message compressed")

        return hidden_message + DELIMITER_SUFFIX.encode()

    def decode(self, data: bytes, password: str | None) -> str:
        """Recover the plaintext message from a hidden payload.

        Args:
            data: The raw bytes extracted from the image. Only the part
                up to the first end delimiter is used; if the delimiter
                is missing, the whole input is used.
            password: If truthy, the payload is decrypted with a key
                derived from this password before decoding. An empty
                string or None decodes the payload without decryption.

        Returns:
            The recovered plaintext message.

        Raises:
            InvalidPasswordError: If a password is provided but is not
                valid.
            DecryptionError: If the password is wrong or the data is
                corrupted.
        """
        delimiter = DELIMITER_SUFFIX.encode()
        end = data.find(delimiter)
        message_bytes = data[:end] if end != -1 else data
        logger.debug(f"Extracted message bytes: {len(message_bytes)} bytes")

        decompressed = decompress_message(bytes(message_bytes))

        if password:
            logger.info("Decrypting message")
            logger.info("Decryption procedure begins")
            raw = base64.b64decode(decompressed)
            parsed_password = Password.parse(password)
            decrypted = self._cipher.decrypt(raw, parsed_password)
            return decrypted.decode()

        logger.info("No password provided, decoding without decryption")
        return decompressed.decode()
