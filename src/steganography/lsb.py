import numpy as np

from src.exceptions import MessageTooLargeError
from src.logger import logger


class SequentialLsbStrategy:
    """Embeds and extracts data in the least significant bit of each byte.

    Implements the ``EmbeddingStrategy`` protocol. Payload bits are
    written into the pixel bytes sequentially, starting from the first
    one, most significant bit first. Unused bits after the payload are
    overwritten with random noise to make statistical detection harder.
    """

    def embed(self, pixels: np.ndarray, payload: bytes) -> np.ndarray:
        """Hide a payload in the pixel LSBs and add random noise.

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
        binary_message = self._bytes_to_bits_binary_list(payload)

        # Flatten the pixel arrays
        flat_data = pixels.flatten()

        logger.info(f"Embedding message: size={len(binary_message)} bits")

        # Check if message will fit
        if len(binary_message) > len(flat_data):
            raise MessageTooLargeError(
                f"Message too large! ({len(binary_message)} bit) "
                f"- Max capacity: {len(flat_data)} bit."
            )

        # Add message and random noise
        self._modify_lsb(flat_data, binary_message)
        self._add_noise(flat_data, len(binary_message))

        # Reshape back to an image pixel array
        return np.reshape(flat_data, pixels.shape)

    def extract(self, pixels: np.ndarray) -> bytes:
        """Recover the raw byte stream hidden in the pixel LSBs.

        Args:
            pixels: NumPy array of image pixel data.

        Returns:
            A byte stream of which the embedded payload is a prefix.
        """
        lsb_data = self._extract_lsb_data(pixels)
        logger.debug(f"Extracted LSB data: {len(lsb_data)} bits")

        return self._process_extracted_data(lsb_data)

    def _bytes_to_bits_binary_list(self, byte_data: bytes) -> np.ndarray:
        """Convert bytes data to a bit array.

        Args:
            byte_data: Bytes to convert.

        Returns:
            NumPy array of bits (0s and 1s).
        """
        logger.debug(f"Converting {len(byte_data)} bytes to binary list")
        return np.unpackbits(np.frombuffer(byte_data, dtype=np.uint8))

    def _modify_lsb(
        self, flat_data: np.ndarray, b_message: np.ndarray
    ) -> None:
        """Write the message bits into the pixel LSBs.

        Args:
            flat_data: Flattened NumPy array of image pixels, modified
                in place.
            b_message: NumPy array of binary bits representing the
                message.
        """
        logger.debug(
            f"Modifying LSB of {len(flat_data)} pixels with "
            f"{len(b_message)} message bits"
        )
        target_data = flat_data[: len(b_message)]

        # Set the LSBs to 0 and then insert message bits
        target_data = target_data & ~np.uint8(1) | b_message

        flat_data[: len(b_message)] = target_data

    def _add_noise(self, flat_data: np.ndarray, used_bits: int) -> None:
        """Add random noise to unused LSB bits to make detection harder.

        Args:
            flat_data: Flattened NumPy array of image pixels, modified
                in place.
            used_bits: Number of bits used for message encoding.
        """
        logger.debug(
            f"Adding noise to {len(flat_data) - used_bits} unused bits"
        )
        unused_data = flat_data[used_bits:]

        # Generate a random binary mask (0 or 1) for flipping LSBs
        noise_mask = np.random.choice(
            [0, 1], size=unused_data.shape, p=[0.7, 0.3]
        ).astype(np.uint8)

        # Apply the noise mask using XOR (flips LSB randomly)
        unused_data ^= noise_mask

        flat_data[used_bits:] = unused_data

    def _extract_lsb_data(self, image_data: np.ndarray) -> np.ndarray:
        """Extract the least significant bits from the image data.

        Args:
            image_data: NumPy array of image data.

        Returns:
            NumPy array of extracted LSB bits.
        """
        logger.debug(
            f"Extracting LSB from image data: shape={image_data.shape}"
        )

        # Flatten the pixel arrays
        flat_data = image_data.flatten()

        # Extract just the least significant bit from each byte
        lsb_bits = flat_data & 1

        return lsb_bits

    def _process_extracted_data(self, lsb_data: np.ndarray) -> bytes:
        """Pack the extracted LSB bits into bytes.

        Args:
            lsb_data: Raw extracted data from the image LSB.

        Returns:
            The packed bytes, ready to be decoded by the payload codec.
        """
        logger.debug(f"Processing extracted LSB data: {len(lsb_data)} bits")

        # Packs binary-valued array into 8-bits array.
        return np.packbits(lsb_data).tobytes()
