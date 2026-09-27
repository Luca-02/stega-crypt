import inspect
import os
from dataclasses import FrozenInstanceError
from tempfile import TemporaryDirectory
from unittest import TestCase

import numpy as np
from PIL import Image

from src.exceptions import (
    InputMessageConflictError,
    InvalidPasswordError,
    MessageTooLargeError,
    NoMessageFoundError,
)
from src.service import (
    DecodeRequest,
    EncodeRequest,
    SteganographyService,
    create_default_service,
)
from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message
from src.steganography.payload_codec import PayloadCodec
from tests.fakes import FakeCipher


class LoadFailure(Exception):
    """Sentinel exception used to prove that load happens before other
    steps, without depending on any real image store behaviour.
    """


class FakeStrategy:
    """Deterministic embedding strategy that records every call it gets."""

    def __init__(
        self,
        calls: list,
        extract_return: bytes = b"",
        embed_error: Exception | None = None,
    ) -> None:
        self._calls = calls
        self._extract_return = extract_return
        self._embed_error = embed_error

    def embed(self, pixels: np.ndarray, payload: bytes) -> np.ndarray:
        self._calls.append(("embed", payload))
        if self._embed_error is not None:
            raise self._embed_error
        return pixels

    def extract(self, pixels: np.ndarray) -> bytes:
        self._calls.append(("extract",))
        return self._extract_return


class FakeImageStore:
    """Deterministic image store that records every call it gets."""

    def __init__(
        self,
        calls: list,
        pixels: np.ndarray | None = None,
        save_return: str = "saved-image-path",
        load_error: Exception | None = None,
    ) -> None:
        self._calls = calls
        self._pixels = (
            pixels
            if pixels is not None
            else np.zeros((2, 2, 3), dtype=np.uint8)
        )
        self._save_return = save_return
        self._load_error = load_error

    def load(self, image_path: str) -> np.ndarray:
        self._calls.append(("load", image_path))
        if self._load_error is not None:
            raise self._load_error
        return self._pixels

    def save(
        self,
        pixels: np.ndarray,
        output_path: str,
        file_name: str,
        image_format: str,
    ) -> str:
        self._calls.append(("save", output_path, file_name, image_format))
        return self._save_return


class TestEncodeRequest(TestCase):
    def test_defaults_match_encode_message_signature(self):
        signature = inspect.signature(encode_message)
        request = EncodeRequest(image_path="img.png")

        for name in (
            "message",
            "message_path",
            "output_path",
            "image_name",
            "compress",
            "password",
        ):
            self.assertEqual(
                signature.parameters[name].default,
                getattr(request, name),
            )

    def test_is_immutable(self):
        request = EncodeRequest(image_path="img.png")

        with self.assertRaises(FrozenInstanceError):
            request.image_path = "other.png"

    def test_password_excluded_from_repr(self):
        request = EncodeRequest(image_path="img.png", password="secret")

        self.assertNotIn("secret", repr(request))


class TestDecodeRequest(TestCase):
    def test_defaults_match_decode_message_signature(self):
        signature = inspect.signature(decode_message)
        request = DecodeRequest(image_path="img.png")

        for name in (
            "output_path",
            "message_name",
            "save_message",
            "password",
        ):
            self.assertEqual(
                signature.parameters[name].default,
                getattr(request, name),
            )

    def test_is_immutable(self):
        request = DecodeRequest(image_path="img.png")

        with self.assertRaises(FrozenInstanceError):
            request.image_path = "other.png"

    def test_password_excluded_from_repr(self):
        request = DecodeRequest(image_path="img.png", password="secret")

        self.assertNotIn("secret", repr(request))


class TestSteganographyServiceEncode(TestCase):
    def setUp(self) -> None:
        self.calls: list = []
        self.codec = PayloadCodec(FakeCipher())

    def _make_service(self, strategy=None, image_store=None):
        strategy = strategy or FakeStrategy(self.calls)
        image_store = image_store or FakeImageStore(self.calls)
        return SteganographyService(self.codec, strategy, image_store)

    def test_call_order_is_load_then_embed_then_save(self):
        service = self._make_service()

        service.encode(EncodeRequest(image_path="photo.png", message="hello"))

        call_types = [call[0] for call in self.calls]
        self.assertEqual(["load", "embed", "save"], call_types)

    def test_embed_receives_the_codec_payload(self):
        service = self._make_service()

        service.encode(
            EncodeRequest(
                image_path="photo.png", message="hello", compress=False
            )
        )

        expected_payload = self.codec.encode(
            "hello", password=None, compress=False
        )
        embed_call = next(call for call in self.calls if call[0] == "embed")
        self.assertEqual(expected_payload, embed_call[1])

    def test_save_receives_expected_arguments_and_return_value(self):
        image_store = FakeImageStore(self.calls, save_return="the-new-path")
        service = self._make_service(image_store=image_store)

        result = service.encode(
            EncodeRequest(
                image_path="photo.png",
                message="hello",
                output_path="out",
                image_name="custom",
            )
        )

        save_call = next(call for call in self.calls if call[0] == "save")
        self.assertEqual(("save", "out", "custom", "png"), save_call)
        self.assertEqual("the-new-path", result)

    def test_default_image_name_and_lowercase_format(self):
        image_store = FakeImageStore(self.calls)
        service = self._make_service(image_store=image_store)

        service.encode(EncodeRequest(image_path="photo.PNG", message="hello"))

        save_call = next(call for call in self.calls if call[0] == "save")
        self.assertEqual("photo-modified", save_call[2])
        self.assertEqual("png", save_call[3])

    def test_message_and_message_path_conflict_before_load(self):
        service = self._make_service()

        with self.assertRaises(InputMessageConflictError):
            service.encode(
                EncodeRequest(
                    image_path="photo.png",
                    message="hello",
                    message_path="message.txt",
                )
            )

        self.assertEqual([], self.calls)

    def test_empty_message_before_load(self):
        service = self._make_service()

        with self.assertRaises(NoMessageFoundError):
            service.encode(EncodeRequest(image_path="photo.png", message=""))

        self.assertEqual([], self.calls)

    def test_load_error_happens_before_password_validation(self):
        image_store = FakeImageStore(self.calls, load_error=LoadFailure())
        service = self._make_service(image_store=image_store)

        with self.assertRaises(LoadFailure):
            service.encode(
                EncodeRequest(
                    image_path="photo.png",
                    message="hello",
                    password="   ",
                )
            )

    def test_invalid_password_happens_before_embed(self):
        service = self._make_service()

        with self.assertRaises(InvalidPasswordError):
            service.encode(
                EncodeRequest(
                    image_path="photo.png",
                    message="hello",
                    password="   ",
                )
            )

        self.assertEqual(
            [], [call for call in self.calls if call[0] == "embed"]
        )

    def test_message_too_large_happens_before_save(self):
        strategy = FakeStrategy(self.calls, embed_error=MessageTooLargeError())
        service = self._make_service(strategy=strategy)

        with self.assertRaises(MessageTooLargeError):
            service.encode(
                EncodeRequest(image_path="photo.png", message="hello")
            )

        self.assertEqual(
            [], [call for call in self.calls if call[0] == "save"]
        )

    def test_message_loaded_from_message_path(self):
        service = self._make_service()

        with TemporaryDirectory() as tmp_dir:
            message_path = os.path.join(tmp_dir, "message.txt")
            with open(message_path, "w") as message_file:
                message_file.write("from file")

            service.encode(
                EncodeRequest(
                    image_path="photo.png", message_path=message_path
                )
            )

        expected_payload = self.codec.encode(
            "from file", password=None, compress=True
        )
        embed_call = next(call for call in self.calls if call[0] == "embed")
        self.assertEqual(expected_payload, embed_call[1])


class TestSteganographyServiceDecode(TestCase):
    def setUp(self) -> None:
        self.calls: list = []
        self.codec = PayloadCodec(FakeCipher())
        self.message = "Hello World!"
        self.packed_bytes = self.codec.encode(
            self.message, password=None, compress=False
        )

    def _make_service(self, strategy=None, image_store=None):
        strategy = strategy or FakeStrategy(
            self.calls, extract_return=self.packed_bytes
        )
        image_store = image_store or FakeImageStore(self.calls)
        return SteganographyService(self.codec, strategy, image_store)

    def test_call_order_is_load_then_extract(self):
        service = self._make_service()

        service.decode(DecodeRequest(image_path="photo.png"))

        call_types = [call[0] for call in self.calls]
        self.assertEqual(["load", "extract"], call_types)

    def test_returns_message_when_not_saving(self):
        service = self._make_service()

        result = service.decode(
            DecodeRequest(image_path="photo.png", save_message=False)
        )

        self.assertEqual(self.message, result)

    def test_saves_message_with_default_name(self):
        service = self._make_service()

        with TemporaryDirectory() as tmp_dir:
            result = service.decode(
                DecodeRequest(
                    image_path="photo.png",
                    output_path=tmp_dir,
                    save_message=True,
                )
            )

            expected_path = os.path.join(tmp_dir, "photo-message.txt")
            self.assertEqual(expected_path, result)
            with open(expected_path) as saved_file:
                self.assertEqual(self.message, saved_file.read())

    def test_saves_message_with_explicit_name(self):
        service = self._make_service()

        with TemporaryDirectory() as tmp_dir:
            result = service.decode(
                DecodeRequest(
                    image_path="photo.png",
                    output_path=tmp_dir,
                    message_name="custom-name",
                    save_message=True,
                )
            )

            self.assertEqual(os.path.join(tmp_dir, "custom-name.txt"), result)


class TestCreateDefaultService(TestCase):
    def test_wires_the_default_collaborators(self):
        service = create_default_service()

        self.assertIsInstance(service, SteganographyService)

    def test_roundtrip_with_real_components(self):
        service = create_default_service()
        message = "Secret message"
        password = "password123"

        with TemporaryDirectory() as tmp_dir:
            image_path = os.path.join(tmp_dir, "cover.png")
            Image.new("RGB", (100, 100), color=(10, 20, 30)).save(
                image_path, "png"
            )

            new_image_path = service.encode(
                EncodeRequest(
                    image_path=image_path,
                    message=message,
                    output_path=tmp_dir,
                    image_name="encoded",
                    compress=False,
                    password=password,
                )
            )

            decoded_message = service.decode(
                DecodeRequest(image_path=new_image_path, password=password)
            )

            self.assertEqual(message, decoded_message)
