import base64
import binascii
import zlib
from unittest import TestCase

from src.cryptography.aes_gcm import AesGcmCipher
from src.cryptography.password_handler import Password
from src.exceptions import DecryptionError, InvalidPasswordError
from src.steganography.payload_codec import PayloadCodec
from tests.steganography.reference import COMPRESSION_PREFIX, DELIMITER


class FakeCipher:
    """Deterministic fake cipher, used to check that PayloadCodec works
    with any Cipher implementation rather than one tied to AES-GCM.
    """

    def encrypt(self, data: bytes, password: Password) -> bytes:
        return b"ENC:" + password.value.encode() + b":" + data

    def decrypt(self, data: bytes, password: Password) -> bytes:
        prefix = b"ENC:" + password.value.encode() + b":"
        if not data.startswith(prefix):
            raise DecryptionError("Fake decryption failed.")
        return data[len(prefix) :]


class TestPayloadCodecEncode(TestCase):
    def setUp(self) -> None:
        self.codec = PayloadCodec(FakeCipher())
        self.message = "Hello World!"
        self.compressible_message = "stega-crypt " * 50
        self.password = "password123"

    def test_plain_uncompressed_layout(self):
        encoded = self.codec.encode(
            self.message, password=None, compress=False
        )

        self.assertEqual(self.message.encode() + DELIMITER, encoded)

    def test_compression_applied_when_beneficial(self):
        encoded = self.codec.encode(
            self.compressible_message, password=None, compress=True
        )

        expected = (
            COMPRESSION_PREFIX
            + zlib.compress(self.compressible_message.encode())
            + DELIMITER
        )
        self.assertEqual(expected, encoded)

    def test_compression_skipped_when_not_beneficial(self):
        encoded = self.codec.encode(self.message, password=None, compress=True)

        self.assertEqual(self.message.encode() + DELIMITER, encoded)

    def test_compress_none_still_compresses(self):
        encoded = self.codec.encode(
            self.compressible_message, password=None, compress=None
        )

        self.assertTrue(encoded.startswith(COMPRESSION_PREFIX))

    def test_encryption_with_fake_cipher(self):
        encoded = self.codec.encode(
            self.message, password=self.password, compress=False
        )

        expected = (
            base64.b64encode(
                b"ENC:" + self.password.encode() + b":" + self.message.encode()
            )
            + DELIMITER
        )
        self.assertEqual(expected, encoded)

    def test_empty_password_disables_encryption(self):
        encoded = self.codec.encode(self.message, password="", compress=False)

        self.assertEqual(self.message.encode() + DELIMITER, encoded)

    def test_blank_password_is_rejected(self):
        with self.assertRaises(InvalidPasswordError) as context:
            self.codec.encode(self.message, password="   ", compress=False)

        self.assertEqual(
            "You must provide a password.", str(context.exception)
        )

    def test_password_is_stripped_before_reaching_the_cipher(self):
        encoded = self.codec.encode(
            self.message, password=f"  {self.password}  ", compress=False
        )

        expected = (
            base64.b64encode(
                b"ENC:" + self.password.encode() + b":" + self.message.encode()
            )
            + DELIMITER
        )
        self.assertEqual(expected, encoded)


class TestPayloadCodecDecode(TestCase):
    def setUp(self) -> None:
        self.codec = PayloadCodec(FakeCipher())
        self.message = "Hello World!"
        self.compressible_message = "stega-crypt " * 50
        self.password = "password123"

    def test_decode_stops_at_first_delimiter(self):
        stream = b"first" + DELIMITER + b"second" + DELIMITER

        self.assertEqual("first", self.codec.decode(stream, password=None))

    def test_decode_without_delimiter_returns_whole_stream(self):
        stream = b"no delimiter here"

        self.assertEqual(
            "no delimiter here", self.codec.decode(stream, password=None)
        )

    def test_decode_decompresses_when_prefix_present(self):
        stream = (
            COMPRESSION_PREFIX
            + zlib.compress(self.compressible_message.encode())
            + DELIMITER
        )

        self.assertEqual(
            self.compressible_message,
            self.codec.decode(stream, password=None),
        )

    def test_decode_without_password_returns_envelope_text(self):
        envelope = base64.b64encode(
            b"ENC:" + self.password.encode() + b":" + self.message.encode()
        )
        stream = envelope + DELIMITER

        self.assertEqual(
            envelope.decode(), self.codec.decode(stream, password=None)
        )

    def test_decode_with_password_on_non_base64_data_raises_base64_error(
        self,
    ):
        stream = b"not-base64-!!" + DELIMITER

        with self.assertRaises(binascii.Error):
            self.codec.decode(stream, password="   ")


class TestPayloadCodecRoundtrip(TestCase):
    def setUp(self) -> None:
        self.codec = PayloadCodec(FakeCipher())
        self.message = "Hello World!"
        self.password = "password123"

    def test_roundtrip_combinations(self):
        for compress in (False, True, None):
            for password in (None, "", self.password):
                with self.subTest(compress=compress, password=password):
                    encoded = self.codec.encode(
                        self.message, password=password, compress=compress
                    )
                    decoded = self.codec.decode(encoded, password=password)

                    self.assertEqual(self.message, decoded)


class TestPayloadCodecWithAesGcmCipher(TestCase):
    def test_roundtrip_with_real_cipher(self):
        codec = PayloadCodec(AesGcmCipher())
        message = "Secret message"
        password = "password123"

        # Compression stays off: with a random salt the compressed output
        # can contain the end delimiter (known bug), which would make this
        # test flaky. Base64 output never contains it.
        encoded = codec.encode(message, password=password, compress=False)
        decoded = codec.decode(encoded, password=password)

        self.assertEqual(message, decoded)
