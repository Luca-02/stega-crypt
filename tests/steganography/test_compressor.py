import zlib
from unittest import TestCase

from src.steganography.compressor import compress_message, decompress_message
from tests.steganography.reference import COMPRESSION_PREFIX


class TestCompressor(TestCase):
    def setUp(self) -> None:
        self.compressible = b"stega-crypt " * 50
        self.incompressible = b"abc"

    def test_compress_adds_prefix_when_beneficial(self):
        self.assertEqual(
            COMPRESSION_PREFIX + zlib.compress(self.compressible),
            compress_message(self.compressible),
        )

    def test_compress_returns_original_when_not_beneficial(self):
        self.assertEqual(
            self.incompressible, compress_message(self.incompressible)
        )

    def test_decompress_prefixed_data(self):
        compressed = COMPRESSION_PREFIX + zlib.compress(self.compressible)
        self.assertEqual(self.compressible, decompress_message(compressed))

    def test_decompress_leaves_unprefixed_data_unchanged(self):
        self.assertEqual(
            self.incompressible, decompress_message(self.incompressible)
        )

    def test_decompress_is_triggered_by_prefix_alone(self):
        # Known limitation kept by the refactor: plain data starting with
        # the prefix is treated as compressed.
        with self.assertRaises(zlib.error):
            decompress_message(COMPRESSION_PREFIX + b"plain text")
