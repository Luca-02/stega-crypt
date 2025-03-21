from re import match

from ..config import MIN_PASSWORD_LENGTH


def clean_password(password: str) -> str:
    """
    Clean a taken password.

    :param password: The password to clean.
    :return: The cleaned password.
    """
    return password.strip()


def is_valid_password(password: str) -> bool:
    """
    Soft password validation:
        - Should be at least MIN_PASSWORD_LENGTH characters long.
        - Should not contain spaces.

    :param password: The password to validate.
    :return: A match if it's a valid password, otherwise None
    """
    if not password:
        return False

    pattern = rf'^\S{{{MIN_PASSWORD_LENGTH},}}$'
    return bool(match(pattern, password))
