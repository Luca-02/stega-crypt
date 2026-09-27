from unittest import TestCase

import numpy as np

from src.exceptions import MessageTooLargeError
from src.steganography.embedding import EmbeddingStrategy
from src.steganography.lsb import SequentialLsbStrategy


class TestSequentialLsbStrategy(TestCase):
    def setUp(self) -> None:
        self.strategy: EmbeddingStrategy = SequentialLsbStrategy()
        self.pixels_2d = self._build_pixels((8, 8))
        self.pixels_rgb = self._build_pixels((8, 8, 3))
        self.pixels_rgba = self._build_pixels((8, 8, 4))
        self.payload = b"hi"

    @staticmethod
    def _build_pixels(shape: tuple) -> np.ndarray:
        size = int(np.prod(shape))
        return (np.arange(size) % 251).astype(np.uint8).reshape(shape)

    def test_embedded_bits_match_payload_msb_first(self):
        embedded = self.strategy.embed(self.pixels_rgb, self.payload)

        payload_bits = np.unpackbits(
            np.frombuffer(self.payload, dtype=np.uint8)
        )
        flat_embedded = embedded.flatten()
        used = flat_embedded[: len(payload_bits)]

        np.testing.assert_array_equal(used & 1, payload_bits)

    def test_upper_bits_of_every_byte_are_unchanged(self):
        embedded = self.strategy.embed(self.pixels_rgb, self.payload)

        flat_original = self.pixels_rgb.flatten()
        flat_embedded = embedded.flatten()

        np.testing.assert_array_equal(
            flat_original & 0xFE, flat_embedded & 0xFE
        )

    def test_noise_only_touches_bits_after_the_payload(self):
        state = np.random.get_state()
        try:
            np.random.seed(0)
            embedded = self.strategy.embed(self.pixels_rgb, self.payload)
        finally:
            np.random.set_state(state)

        payload_bits = np.unpackbits(
            np.frombuffer(self.payload, dtype=np.uint8)
        )
        used_bits = len(payload_bits)
        flat_original = self.pixels_rgb.flatten()
        flat_embedded = embedded.flatten()

        # The LSBs of the used region hold the payload, not noise.
        np.testing.assert_array_equal(
            flat_embedded[:used_bits] & 1, payload_bits
        )

        # The unused region is noise: it must differ from the cover in
        # some of its LSBs.
        noise_changed = (
            flat_original[used_bits:] ^ flat_embedded[used_bits:]
        ) & 1
        self.assertTrue(np.any(noise_changed))

    def test_same_seed_produces_same_output(self):
        state = np.random.get_state()
        try:
            np.random.seed(42)
            first = self.strategy.embed(self.pixels_rgb, self.payload)
            np.random.seed(42)
            second = self.strategy.embed(self.pixels_rgb, self.payload)
        finally:
            np.random.set_state(state)

        np.testing.assert_array_equal(first, second)

    def test_embed_does_not_mutate_input(self):
        original = self.pixels_rgb.copy()

        self.strategy.embed(self.pixels_rgb, self.payload)

        np.testing.assert_array_equal(original, self.pixels_rgb)

    def test_embed_preserves_shape_and_dtype_for_2d_pixels(self):
        embedded = self.strategy.embed(self.pixels_2d, self.payload)

        self.assertEqual(embedded.shape, self.pixels_2d.shape)
        self.assertEqual(embedded.dtype, self.pixels_2d.dtype)

    def test_embed_preserves_shape_and_dtype_for_rgb_pixels(self):
        embedded = self.strategy.embed(self.pixels_rgb, self.payload)

        self.assertEqual(embedded.shape, self.pixels_rgb.shape)
        self.assertEqual(embedded.dtype, self.pixels_rgb.dtype)

    def test_embed_preserves_shape_and_dtype_for_rgba_pixels(self):
        embedded = self.strategy.embed(self.pixels_rgba, self.payload)

        self.assertEqual(embedded.shape, self.pixels_rgba.shape)
        self.assertEqual(embedded.dtype, self.pixels_rgba.dtype)

    def test_embed_payload_filling_exact_capacity(self):
        capacity_bytes = self.pixels_rgb.size // 8
        payload = b"A" * capacity_bytes

        embedded = self.strategy.embed(self.pixels_rgb, payload)

        self.assertEqual(embedded.shape, self.pixels_rgb.shape)

    def test_embed_payload_one_byte_over_capacity_raises(self):
        capacity_bytes = self.pixels_rgb.size // 8
        payload = b"A" * (capacity_bytes + 1)
        message_bits = len(payload) * 8
        max_capacity = self.pixels_rgb.size

        with self.assertRaises(MessageTooLargeError) as context:
            self.strategy.embed(self.pixels_rgb, payload)

        self.assertEqual(
            f"Message too large! ({message_bits} bit) "
            f"- Max capacity: {max_capacity} bit.",
            str(context.exception),
        )

    def test_extract_starts_with_the_embedded_payload(self):
        embedded = self.strategy.embed(self.pixels_rgb, self.payload)

        extracted = self.strategy.extract(embedded)

        self.assertTrue(extracted.startswith(self.payload))

    def test_extract_length_matches_image_capacity_in_bytes(self):
        extracted = self.strategy.extract(self.pixels_rgb)

        self.assertEqual(self.pixels_rgb.size // 8, len(extracted))

    def test_roundtrip(self):
        embedded = self.strategy.embed(self.pixels_rgb, self.payload)

        extracted = self.strategy.extract(embedded)

        self.assertTrue(extracted.startswith(self.payload))
