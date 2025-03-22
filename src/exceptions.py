class MessageFileNotFoundError(FileNotFoundError):
    pass


class ImageFileNotFoundError(FileNotFoundError):
    pass


class MessageTooLargeError(Exception):
    pass


class FileAlreadyExistsError(FileExistsError):
    pass


class NoMessageFoundError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class DecryptionError(Exception):
    pass
