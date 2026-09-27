import base64
import binascii
import os
import random
import zlib

import numpy as np
import pytest
from PIL import Image

from src.exceptions import InvalidPasswordError, MessageTooLargeError
from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message
from tests.steganography import reference
from tests.steganography.base_test_stenography import BaseTestSteganography
from tests.steganography.reference import COMPRESSION_PREFIX, DELIMITER


def colliding_message() -> str:
    """Build a message whose zlib output contains the end delimiter.

    Returns:
        A deterministic, compressible message.
    """
    rng = random.Random(344)
    words = [
        "the",
        "quick",
        "brown",
        "fox",
        "jumps",
        "over",
        "lazy",
        "dog",
        "secret",
        "message",
    ]
    return " ".join(rng.choice(words) for _ in range(120))


class TestPayloadFormat(BaseTestSteganography):
    def encode(self, **kwargs) -> str:
        return encode_message(
            image_path=self.image_path,
            output_path=self.output_path,
            image_name=self.image_name,
            **kwargs,
        )

    def save_stream_image(self, stream: bytes) -> str:
        pixels = reference.write_lsb_stream(
            reference.load_pixels(self.image_path), stream
        )
        path = os.path.join(self.dir.name, "crafted.png")
        Image.fromarray(pixels).save(path)
        return path

    def test_plain_payload_layout(self):
        path = self.encode(message=self.message, compress=False)

        self.assertTrue(
            reference.read_lsb_stream(path).startswith(
                self.message.encode() + DELIMITER
            )
        )

    def test_compressed_payload_layout(self):
        path = self.encode(message=self.long_message, compress=True)

        expected = (
            COMPRESSION_PREFIX
            + zlib.compress(self.long_message.encode())
            + DELIMITER
        )
        self.assertTrue(reference.read_lsb_stream(path).startswith(expected))

    def test_compress_none_still_compresses(self):
        path = self.encode(message=self.long_message, compress=None)

        self.assertTrue(
            reference.read_lsb_stream(path).startswith(COMPRESSION_PREFIX)
        )

    def test_short_message_is_not_compressed_when_not_beneficial(self):
        path = self.encode(message=self.message, compress=True)

        self.assertTrue(
            reference.read_lsb_stream(path).startswith(
                self.message.encode() + DELIMITER
            )
        )

    def test_encrypted_payload_layout(self):
        path = self.encode(
            message=self.message, password=self.password, compress=False
        )

        stream = reference.read_lsb_stream(path)
        envelope = stream[: stream.index(DELIMITER)]
        self.assertEqual(
            reference.ENVELOPE_OVERHEAD + len(self.message.encode()),
            len(base64.b64decode(envelope, validate=True)),
        )
        self.assertEqual(
            self.message.encode(), reference.decrypt(envelope, self.password)
        )

    def test_encrypted_payload_is_compressed_after_encryption(self):
        path = self.encode(
            message=self.long_message, password=self.password, compress=True
        )

        stream = reference.read_lsb_stream(path)
        self.assertTrue(stream.startswith(COMPRESSION_PREFIX))
        decompressor = zlib.decompressobj()
        envelope = decompressor.decompress(stream[len(COMPRESSION_PREFIX) :])
        self.assertTrue(decompressor.unused_data.startswith(DELIMITER))
        self.assertEqual(
            self.long_message.encode(),
            reference.decrypt(envelope, self.password),
        )

    def test_password_is_stripped_before_key_derivation(self):
        path = self.encode(
            message=self.message,
            password=f"  {self.password}  ",
            compress=False,
        )

        stream = reference.read_lsb_stream(path)
        envelope = stream[: stream.index(DELIMITER)]
        self.assertEqual(
            self.message.encode(), reference.decrypt(envelope, self.password)
        )

    def test_decode_without_password_returns_envelope_text(self):
        self.encode(
            message=self.message, password=self.password, compress=False
        )

        decoded = decode_message(self.encoded_image_path)

        self.assertEqual(
            self.message.encode(),
            reference.decrypt(decoded.encode(), self.password),
        )

    def test_decode_with_password_on_plain_message(self):
        self.encode(message=self.message, compress=False)

        with self.assertRaises(binascii.Error):
            decode_message(self.encoded_image_path, password=self.password)

    def test_empty_password_disables_encryption(self):
        path = self.encode(message=self.message, password="", compress=False)

        self.assertTrue(
            reference.read_lsb_stream(path).startswith(
                self.message.encode() + DELIMITER
            )
        )

    def test_blank_password_is_rejected(self):
        with self.assertRaises(InvalidPasswordError) as context:
            self.encode(message=self.message, password="   ")

        self.assertEqual(
            "You must provide a password.", str(context.exception)
        )

    def test_decode_independently_built_encrypted_payload(self):
        envelope = reference.encrypt(
            self.message.encode(),
            self.password,
            salt=bytes(range(16)),
            nonce=bytes(range(16, 32)),
        )
        path = self.save_stream_image(envelope + DELIMITER)

        self.assertEqual(
            self.message, decode_message(path, password=self.password)
        )

    def test_decode_independently_built_compressed_payload(self):
        stream = (
            COMPRESSION_PREFIX
            + zlib.compress(self.long_message.encode())
            + DELIMITER
        )
        path = self.save_stream_image(stream)

        self.assertEqual(self.long_message, decode_message(path))

    def test_decode_stops_at_first_delimiter(self):
        path = self.save_stream_image(
            b"first" + DELIMITER + b"second" + DELIMITER
        )

        self.assertEqual("first", decode_message(path))

    def test_decode_without_delimiter_returns_whole_stream(self):
        capacity = self.img_size[0] * self.img_size[1] * 3 // 8
        path = self.save_stream_image(b"A" * capacity)

        self.assertEqual("A" * capacity, decode_message(path))

    def test_noise_only_touches_unused_lsb(self):
        state = np.random.get_state()
        try:
            np.random.seed(0)
            path = self.encode(message=self.message, compress=False)
        finally:
            np.random.set_state(state)

        cover = reference.load_pixels(self.image_path).flatten()
        encoded = reference.load_pixels(path).flatten()
        changed = cover ^ encoded
        self.assertFalse(np.any(changed & 0xFE))

        used_bits = len(self.message.encode() + DELIMITER) * 8
        flipped = np.count_nonzero(changed[used_bits:]) / (
            len(cover) - used_bits
        )
        self.assertTrue(0.25 < flipped < 0.35)

    def test_message_too_large_error_text(self):
        capacity = self.img_size[0] * self.img_size[1] * 3
        message = "A" * (capacity // 8)
        message_bits = (len(message) + len(DELIMITER)) * 8

        with self.assertRaises(MessageTooLargeError) as context:
            self.encode(message=message, compress=False)

        self.assertEqual(
            f"Message too large! ({message_bits} bit) "
            f"- Max capacity: {capacity} bit.",
            str(context.exception),
        )

    def test_colliding_message_precondition(self):
        data = colliding_message().encode()
        compressed = COMPRESSION_PREFIX + zlib.compress(data)

        self.assertLess(len(compressed), len(data))
        self.assertIn(DELIMITER, compressed)

    @pytest.mark.xfail(
        raises=zlib.error,
        strict=True,
        reason=(
            "Known bug: the end delimiter can occur inside zlib output and "
            "truncate the payload. Planned fix: length-prefixed header."
        ),
    )
    def test_compressed_payload_containing_delimiter_roundtrip(self):
        message = colliding_message()
        self.encode(message=message, compress=True)

        self.assertEqual(message, decode_message(self.encoded_image_path))
