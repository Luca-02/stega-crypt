import os
from dataclasses import dataclass, field

from src.config import (
    DEFAULT_OUTPUT_DIR,
    MESSAGE_NAME_SUFFIX,
    MODIFIED_IMAGE_SUFFIX,
)
from src.cryptography.aes_gcm import AesGcmCipher
from src.exceptions import InputMessageConflictError, NoMessageFoundError
from src.logger import logger
from src.steganography.embedding import EmbeddingStrategy
from src.steganography.file_handler import load_message_file, save_message_file
from src.steganography.image_store import ImageStore, PillowImageStore
from src.steganography.lsb import SequentialLsbStrategy
from src.steganography.payload_codec import PayloadCodec


@dataclass(frozen=True)
class EncodeRequest:
    """Parameters needed to hide a message into an image.

    Attributes:
        image_path: The path to the input image.
        message: Message to hide, when not using a text file.
        message_path: Path to the text file containing the message.
        output_path: The output folder to save the modified image.
        image_name: The name of the new image file. If not specified,
            '-modified' is appended to the original name.
        compress: Whether to compress the message. When True, the message
            is compressed only if that makes it smaller.
        password: The password to encrypt the hidden message. If not
            specified, the message is not encrypted.
    """

    image_path: str
    message: str | None = None
    message_path: str | None = None
    output_path: str | None = DEFAULT_OUTPUT_DIR
    image_name: str | None = None
    compress: bool | None = True
    password: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class DecodeRequest:
    """Parameters needed to extract a hidden message from an image.

    Attributes:
        image_path: The path to the image containing the hidden message.
        output_path: The output folder to save the message.
        message_name: The name of the message file. If not specified, it
            will be '<image_name>-message'.
        save_message: Whether to save the message to a file.
        password: The password to decrypt the hidden message. If not
            specified, the message is not decrypted.
    """

    image_path: str
    output_path: str | None = DEFAULT_OUTPUT_DIR
    message_name: str | None = None
    save_message: bool | None = False
    password: str | None = field(default=None, repr=False)


class SteganographyService:
    """Orchestrates the encode and decode use cases.

    Depends only on the ``PayloadCodec``, ``EmbeddingStrategy`` and
    ``ImageStore`` abstractions, so it can be assembled with any
    combination of cipher, embedding strategy and image format without
    changes to this class.
    """

    def __init__(
        self,
        codec: PayloadCodec,
        strategy: EmbeddingStrategy,
        image_store: ImageStore,
    ) -> None:
        """Initialize the service with its collaborators.

        Args:
            codec: The payload codec used to encode and decode the hidden
                message.
            strategy: The embedding strategy used to hide and recover
                bytes in pixel data.
            image_store: The image store used to load and save images.
        """
        self._codec = codec
        self._strategy = strategy
        self._image_store = image_store

    def encode(self, request: EncodeRequest) -> str:
        """Hide a message into an image with the configured strategy.

        Args:
            request: The encode request parameters.

        Returns:
            Path to the new image file with the embedded hidden message.

        Raises:
            InputMessageConflictError: If both message and message_path are
                given.
            MessageFileNotFoundError: If the message file is not found.
            NoMessageFoundError: If the message is empty.
            ImageFileNotFoundError: If the image file is not found.
            InvalidPasswordError: If the password is not valid.
            MessageTooLargeError: If the message is too large to fit in the
                image.
            FileAlreadyExistsError: If the output file already exists.
            Exception: For any other unexpected error.
        """
        logger.info(
            f"Starting message encoding: image_path={request.image_path}"
        )

        message = request.message
        message_path = request.message_path

        if message and message_path:
            raise InputMessageConflictError(
                "Input message conflict, choose whether to use a string or a text file"
            )

        if message_path:
            logger.info(f"Loading message from file: {message_path}")
            message = load_message_file(message_path)

        if not message:
            raise NoMessageFoundError("You can't use an empty message.")

        logger.info(f"Message loaded: {len(message)} characters")

        image_data = self._image_store.load(request.image_path)
        logger.debug(
            f"Image loaded: shape={image_data.shape}, type={image_data.dtype}"
        )

        hidden_message = self._codec.encode(
            message, request.password, request.compress
        )
        logger.debug(
            f"Hidden message prepared: size={len(hidden_message)} bytes"
        )

        modified_image = self._strategy.embed(image_data, hidden_message)

        image_name = request.image_name
        if image_name is None:
            image_name = _default_name(
                request.image_path, MODIFIED_IMAGE_SUFFIX
            )

        # The output format is taken from the input image extension
        image_format = (
            os.path.splitext(request.image_path)[1].lower().strip(".")
        )

        logger.info(f"Saving modified image: {image_name}.{image_format}")
        return self._image_store.save(
            modified_image, request.output_path, image_name, image_format
        )

    def decode(self, request: DecodeRequest) -> str:
        """Extract a hidden message from an image with the configured strategy.

        Args:
            request: The decode request parameters.

        Returns:
            The hidden message, or the path of the saved message file when
            save_message is True.

        Raises:
            ImageFileNotFoundError: If the image file is not found.
            UnidentifiedImageError: If the file is not a valid image.
            InvalidPasswordError: If the password is not valid.
            DecryptionError: If the password is wrong or the data is
                corrupted.
            FileAlreadyExistsError: If the message file already exists.
            Exception: For any other unexpected error.
        """
        logger.info(
            f"Starting message decoding: image_path={request.image_path}"
        )
        image_data = self._image_store.load(request.image_path)
        logger.debug(
            f"Image loaded: shape={image_data.shape}, type={image_data.dtype}"
        )

        packed_bytes = self._strategy.extract(image_data)

        message = self._codec.decode(packed_bytes, request.password)

        if not request.save_message:
            return message

        message_name = request.message_name
        if message_name is None:
            message_name = _default_name(
                request.image_path, MESSAGE_NAME_SUFFIX
            )

        logger.info(f"Saving message: {message_name}.txt")
        return save_message_file(message, request.output_path, message_name)


def _default_name(image_path: str, suffix: str) -> str:
    """Build a default output name from the input image name.

    Args:
        image_path: Path of the input image.
        suffix: Suffix appended to the image name without extension.

    Returns:
        The image file name without extension, followed by the suffix.
    """
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    return f"{base_name}{suffix}"


def create_default_service() -> SteganographyService:
    """Assemble the default service used by the CLI and public facades.

    Returns:
        A service wired with AES-GCM encryption, sequential LSB embedding
        and Pillow-backed image storage.
    """
    return SteganographyService(
        PayloadCodec(AesGcmCipher()),
        SequentialLsbStrategy(),
        PillowImageStore(),
    )
