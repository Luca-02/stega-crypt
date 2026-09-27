"""Compatibility tests against images produced by the pre-refactor code.

The PNG files in ``tests/fixtures/golden`` were generated once with the
original procedural implementation, using the cover built by
``build_cover`` and the constants below. They must never be regenerated
with newer code: their purpose is to prove that images written by earlier
versions still decode, and that encoding with the same noise seed still
produces the same pixels.
"""

import os
from tempfile import TemporaryDirectory
from unittest import TestCase

import numpy as np
from PIL import Image

from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message
from tests.steganography import reference

GOLDEN_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "fixtures",
    "golden",
)
COVER_SHAPE = (64, 64, 3)
GOLDEN_MESSAGE = "Golden sample message for stega-crypt."
GOLDEN_LONG_MESSAGE = "stega-crypt golden fixture. " * 20
GOLDEN_PASSWORD = "golden-password"
PLAIN_SEED = 0
COMPRESSED_SEED = 1


def build_cover() -> np.ndarray:
    """Build the deterministic cover image used for the golden fixtures.

    Returns:
        An RGB pixel array of shape ``COVER_SHAPE``.
    """
    size = int(np.prod(COVER_SHAPE))
    return (np.arange(size) % 251).astype(np.uint8).reshape(COVER_SHAPE)


def golden_path(name: str) -> str:
    """Return the path of a golden fixture.

    Args:
        name: File name inside the golden fixture directory.

    Returns:
        The absolute path of the fixture.
    """
    return os.path.join(GOLDEN_DIR, name)


class TestGolden(TestCase):
    def setUp(self) -> None:
        self.dir = TemporaryDirectory()
        self.cover_path = os.path.join(self.dir.name, "cover.png")
        Image.fromarray(build_cover()).save(self.cover_path)

    def tearDown(self) -> None:
        self.dir.cleanup()

    def encode_with_seed(self, seed: int, **kwargs) -> str:
        state = np.random.get_state()
        try:
            np.random.seed(seed)
            return encode_message(
                image_path=self.cover_path,
                output_path=self.dir.name,
                image_name="encoded",
                **kwargs,
            )
        finally:
            np.random.set_state(state)

    def test_decode_golden_plain(self):
        self.assertEqual(
            GOLDEN_MESSAGE, decode_message(golden_path("plain.png"))
        )

    def test_decode_golden_compressed(self):
        self.assertEqual(
            GOLDEN_LONG_MESSAGE, decode_message(golden_path("compressed.png"))
        )

    def test_decode_golden_encrypted_compressed(self):
        self.assertEqual(
            GOLDEN_LONG_MESSAGE,
            decode_message(
                golden_path("encrypted_compressed.png"),
                password=GOLDEN_PASSWORD,
            ),
        )

    def test_encode_matches_golden_plain(self):
        path = self.encode_with_seed(
            PLAIN_SEED, message=GOLDEN_MESSAGE, compress=False
        )

        np.testing.assert_array_equal(
            reference.load_pixels(golden_path("plain.png")),
            reference.load_pixels(path),
        )

    def test_encode_matches_golden_compressed(self):
        path = self.encode_with_seed(
            COMPRESSED_SEED, message=GOLDEN_LONG_MESSAGE, compress=True
        )

        np.testing.assert_array_equal(
            reference.load_pixels(golden_path("compressed.png")),
            reference.load_pixels(path),
        )
