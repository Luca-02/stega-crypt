from typing import Protocol

import numpy as np


class EmbeddingStrategy(Protocol):
    """Common interface for hiding and recovering bytes in pixel data.

    Implementations decide how message bytes are mapped onto pixel bits
    and how they are recovered, but know nothing about the payload
    framing: delimiters, compression and encryption are the
    responsibility of the payload codec, not of the strategy.
    """

    def embed(self, pixels: np.ndarray, payload: bytes) -> np.ndarray:
        """Hide a payload inside pixel data.

        Args:
            pixels: NumPy array of image pixel data. The array is not
                modified.
            payload: The bytes to hide.

        Returns:
            A new array with the same shape and dtype as ``pixels``,
            holding the embedded payload.

        Raises:
            MessageTooLargeError: If the payload does not fit in the
                available pixel data.
        """
        ...

    def extract(self, pixels: np.ndarray) -> bytes:
        """Recover the raw byte stream hidden inside pixel data.

        Args:
            pixels: NumPy array of image pixel data.

        Returns:
            A byte stream of which the embedded payload is a prefix.
            Where the payload ends inside this stream is not known by
            the strategy: locating it is the responsibility of the
            payload codec.
        """
        ...
