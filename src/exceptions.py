class MessageFileNotFoundError(FileNotFoundError):
    pass


class ImageFileNotFoundError(FileNotFoundError):
    pass


class FileAlreadyExistsError(FileExistsError):
    pass


class InputMessageConflictError(ValueError):
    pass


class MessageTooLargeError(ValueError):
    pass


class NoMessageFoundError(ValueError):
    pass


class InvalidPasswordError(ValueError):
    pass


class DecryptionError(Exception):
    pass
