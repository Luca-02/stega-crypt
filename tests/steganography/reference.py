"""Independent reference implementation of the on-image data format.

Nothing here imports from ``src``. Tests use these helpers to check the
bytes that the application writes into and reads from an image against a
fixed specification, so that the format cannot drift during the refactor.
"""

import base64
import hashlib

import numpy as np
from Crypto.Cipher import AES
from PIL import Image

COMPRESSION_PREFIX = b"\x1f\x02"
DELIMITER = b"\x1f\x00"
SALT_SIZE = 16
NONCE_SIZE = 16
TAG_SIZE = 16
ENVELOPE_OVERHEAD = SALT_SIZE + NONCE_SIZE + TAG_SIZE
KDF_HASH = "sha256"
KDF_ITERATIONS = 100000
KEY_SIZE = 32


def load_pixels(image_path: str) -> np.ndarray:
    """Load an image file as a NumPy array.

    Args:
        image_path: Path of the image to load.

    Returns:
        The pixel array of the image.
    """
    with Image.open(image_path) as img:
        return np.array(img)


def read_lsb_stream(image_path: str) -> bytes:
    """Read the byte stream stored in the LSB of every image byte.

    Args:
        image_path: Path of the image to read.

    Returns:
        The bytes obtained by packing the LSBs of the flattened pixels.
    """
    return np.packbits(load_pixels(image_path).flatten() & 1).tobytes()


def write_lsb_stream(pixels: np.ndarray, stream: bytes) -> np.ndarray:
    """Store a byte stream in the leading LSBs of a pixel array.

    Args:
        pixels: Cover pixels. The array is not modified.
        stream: Bytes to store, most significant bit first.

    Returns:
        A new pixel array with the same shape holding the stream.
    """
    bits = np.unpackbits(np.frombuffer(stream, dtype=np.uint8))
    flat = pixels.flatten()
    flat[: len(bits)] = (flat[: len(bits)] & 0xFE) | bits
    return flat.reshape(pixels.shape)


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive the AES key from a password with PBKDF2-HMAC-SHA256.

    Args:
        password: The cleaned password.
        salt: The salt stored in the envelope.

    Returns:
        The derived key.
    """
    return hashlib.pbkdf2_hmac(
        KDF_HASH, password.encode(), salt, KDF_ITERATIONS, dklen=KEY_SIZE
    )


def encrypt(data: bytes, password: str, salt: bytes, nonce: bytes) -> bytes:
    """Build a base64 AES-GCM envelope with a fixed salt and nonce.

    Args:
        data: Plaintext bytes.
        password: The cleaned password.
        salt: A 16 byte salt.
        nonce: A 16 byte nonce.

    Returns:
        ``base64(salt + nonce + ciphertext + tag)``.
    """
    cipher = AES.new(derive_key(password, salt), AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return base64.b64encode(salt + nonce + ciphertext + tag)


def decrypt(envelope: bytes, password: str) -> bytes:
    """Open a base64 AES-GCM envelope.

    Args:
        envelope: ``base64(salt + nonce + ciphertext + tag)``.
        password: The cleaned password.

    Returns:
        The plaintext bytes.

    Raises:
        ValueError: If the tag does not match.
    """
    raw = base64.b64decode(envelope, validate=True)
    salt = raw[:SALT_SIZE]
    nonce = raw[SALT_SIZE : SALT_SIZE + NONCE_SIZE]
    ciphertext = raw[SALT_SIZE + NONCE_SIZE : -TAG_SIZE]
    tag = raw[-TAG_SIZE:]
    cipher = AES.new(derive_key(password, salt), AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
