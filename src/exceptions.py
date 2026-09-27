class MessageFileNotFoundError(FileNotFoundError):
    """Raised when the text file given as the message source does not exist."""


class ImageFileNotFoundError(FileNotFoundError):
    """Raised when the input image file does not exist."""


class FileAlreadyExistsError(FileExistsError):
    """Raised when an output file would overwrite an existing file."""


class InputMessageConflictError(ValueError):
    """Raised when both a message string and a message file are given."""


class MessageTooLargeError(ValueError):
    """Raised when the message payload does not fit in the image."""


class NoMessageFoundError(ValueError):
    """Raised when the message to hide is empty."""


class InvalidPasswordError(ValueError):
    """Raised when a password is invalid or its confirmation does not match."""


class DecryptionError(Exception):
    """Raised when the password is wrong or the encrypted data is corrupted."""
