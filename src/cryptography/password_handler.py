import re
from re import Match


def clean_password(password: str) -> str:
    """
    Clean a taken password.

    :param password: The password to clean.
    :return: The cleaned password.
    """
    return password.strip()


def is_valid_password(password: str) -> Match[str] | None:
    """
    Soft password validation:
        - Should be at least 4 characters long.
        - Should not contain spaces.

    :param password: The password to validate.

    :return: A match if it's a valid password, otherwise None
    """
    reg = r'^\S{4,}$'

    # Compiling regex
    pat = re.compile(reg)

    # Searching regex
    return re.search(pat, password)