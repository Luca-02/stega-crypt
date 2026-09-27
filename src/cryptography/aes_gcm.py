from __future__ import annotations

from dataclasses import dataclass

from Crypto.Cipher import AES

from src.config import NONCE_SIZE_BYTE, SALT_SIZE_BYTE, TAG_SIZE_BYTE
from src.cryptography.derivation import derive_key_from_password, generate_salt
from src.cryptography.password_handler import Password
from src.exceptions import DecryptionError
from src.logger import logger


@dataclass(frozen=True)
class AesGcmEnvelope:
    """The wire format produced and consumed by ``AesGcmCipher``.

    An envelope is the concatenation ``salt + nonce + ciphertext + tag``.
    Slicing it back apart does not validate anything: a truncated or
    malformed blob is expected to yield slices of the wrong length, and
    the failure surfaces later as a ``DecryptionError`` when AES
    itself rejects them.

    Attributes:
        salt: The salt used to derive the encryption key.
        nonce: The nonce used by AES-GCM.
        ciphertext: The encrypted data.
        tag: The AES-GCM authentication tag.
    """

    salt: bytes
    nonce: bytes
    ciphertext: bytes
    tag: bytes

    def to_bytes(self) -> bytes:
        """Serialize the envelope to its wire format.

        Returns:
            The concatenation of salt, nonce, ciphertext and tag.
        """
        return self.salt + self.nonce + self.ciphertext + self.tag

    @classmethod
    def from_bytes(cls, data: bytes) -> AesGcmEnvelope:
        """Slice a wire format blob back into an envelope.

        Args:
            data: The bytes to slice, in ``salt + nonce + ciphertext +
                tag`` order. No length validation is performed: even a
                blob shorter than the fixed-size fields is sliced without
                raising.

        Returns:
            The envelope built from the sliced fields.
        """
        salt = data[:SALT_SIZE_BYTE]
        nonce = data[SALT_SIZE_BYTE : SALT_SIZE_BYTE + NONCE_SIZE_BYTE]
        ciphertext_bottom = SALT_SIZE_BYTE + NONCE_SIZE_BYTE
        ciphertext_upper = -TAG_SIZE_BYTE
        ciphertext = data[ciphertext_bottom:ciphertext_upper]
        tag = data[-TAG_SIZE_BYTE:]
        return cls(salt=salt, nonce=nonce, ciphertext=ciphertext, tag=tag)


class AesGcmCipher:
    """AES-GCM cipher with a PBKDF2-derived key.

    Implements the ``Cipher`` protocol. The key is derived from the
    password and a random salt on every ``encrypt`` call. The password
    is expected to be already validated by the caller.
    """

    def encrypt(self, data: bytes, password: Password) -> bytes:
        """Encrypt data with a key derived from the password.

        Args:
            data: The plaintext bytes to encrypt.
            password: An already validated password.

        Returns:
            The serialized ``AesGcmEnvelope``
            (``salt + nonce + ciphertext + tag``).
        """
        logger.debug("Password validation successful")
        salt = generate_salt(SALT_SIZE_BYTE)
        key = derive_key_from_password(password.value, salt)

        logger.debug("AES-GCM Cipher Creation")
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        envelope = AesGcmEnvelope(
            salt=salt, nonce=cipher.nonce, ciphertext=ciphertext, tag=tag
        )
        encrypted_data = envelope.to_bytes()

        logger.info(f"Encryption completed: data={len(encrypted_data)} bytes")
        return encrypted_data

    def decrypt(self, data: bytes, password: Password) -> bytes:
        """Decrypt an AES-GCM envelope with a key derived from the password.

        Args:
            data: The serialized ``AesGcmEnvelope`` to decrypt.
            password: An already validated password.

        Returns:
            The decrypted plaintext bytes.

        Raises:
            DecryptionError: If the password is wrong or the data is
                corrupted.
        """
        envelope = AesGcmEnvelope.from_bytes(data)

        logger.debug(
            f"Decryption data: "
            f"salt={len(envelope.salt)} byte, "
            f"nonce={len(envelope.nonce)} byte, "
            f"ciphertext={len(envelope.ciphertext)} byte, "
            f"tag={len(envelope.tag)} byte"
        )

        logger.debug("Password validated, key derivation in progress")
        key = derive_key_from_password(password.value, envelope.salt)

        try:
            cipher = AES.new(key, AES.MODE_GCM, nonce=envelope.nonce)
            decrypted_data = cipher.decrypt_and_verify(
                envelope.ciphertext, envelope.tag
            )
            logger.info("Message decryption completed successfully")
            return decrypted_data
        except ValueError:
            raise DecryptionError(
                "Decryption error: incorrect key or corrupted data."
            )
