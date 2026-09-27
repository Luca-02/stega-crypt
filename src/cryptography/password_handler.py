from __future__ import annotations

from dataclasses import dataclass, field
from re import match

from src.config import MIN_PASSWORD_LENGTH
from src.exceptions import InvalidPasswordError
from src.logger import logger


def clean_password(password: str) -> str:
    """Clean a taken password.

    Args:
        password: The password to clean.

    Returns:
        The cleaned password.
    """
    logger.debug("Cleaning password")
    return password.strip()


def is_valid_password(password: str) -> bool:
    """Perform a soft password validation.

    A valid password must be at least MIN_PASSWORD_LENGTH characters
    long and must not contain spaces.

    Args:
        password: The password to validate.

    Returns:
        True if the password is valid, otherwise False.
    """
    logger.debug(f"Validating password (min length: {MIN_PASSWORD_LENGTH})")

    if not password:
        logger.debug("Empty password provided")
        return False

    pattern = rf"^\S{{{MIN_PASSWORD_LENGTH},}}$"
    is_valid = bool(match(pattern, password))

    logger.debug(
        "Password validation: " + ("success" if is_valid else "failed")
    )
    return is_valid


@dataclass(frozen=True)
class Password:
    """A validated password value object.

    Instances are immutable. Create them with ``parse``, which cleans and
    validates the raw value; the constructor itself does not validate.
    The value is excluded from the generated ``repr`` so it never ends up
    in logs or tracebacks.

    Attributes:
        value: The cleaned, validated password value.
    """

    value: str = field(repr=False)

    @classmethod
    def parse(cls, raw: str) -> Password:
        """Clean and validate a raw password string.

        Args:
            raw: The raw password to clean and validate.

        Returns:
            A Password wrapping the cleaned value.

        Raises:
            InvalidPasswordError: If the cleaned password is not valid.
        """
        cleaned = clean_password(raw)
        if not is_valid_password(cleaned):
            raise InvalidPasswordError("You must provide a password.")
        return cls(cleaned)
