from re import match

from src.config import MIN_PASSWORD_LENGTH
from src.logger import logger


def clean_password(password: str) -> str:
    """
    Clean a taken password.

    :param password: The password to clean.
    :return: The cleaned password.
    """
    logger.debug("Cleaning password")
    return password.strip()


def is_valid_password(password: str) -> bool:
    """
    Soft password validation:
        - Should be at least MIN_PASSWORD_LENGTH characters long.
        - Should not contain spaces.

    :param password: The password to validate.
    :return: A match if it's a valid password, otherwise None
    """
    logger.debug(f"Validating password (min length: {MIN_PASSWORD_LENGTH})")

    if not password:
        logger.debug("Empty password provided")
        return False

    pattern = rf"^\S{{{MIN_PASSWORD_LENGTH},}}$"
    is_valid = bool(match(pattern, password))

    logger.debug("Password validation: " + "success" if is_valid else "failed")
    return is_valid
