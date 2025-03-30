from typing import Optional

import art
import click

from src.config import (
    ABOUT_PROJECT,
    DEFAULT_OUTPUT_DIR,
    MESSAGE_NAME_SUFFIX,
    MODIFIED_IMAGE_SUFFIX,
    PROJECT_NAME,
)
from src.exceptions import InvalidPasswordError
from src.logger import logger, setup_logger
from src.steganography.decoder import decode_message
from src.steganography.encoder import encode_message


def __request_password(confirm: bool = False) -> str:
    """
    Request the user to input a password and confirm it.

    :return: The password entered by the user.
    :raises InvalidPasswordError: If the passwords don't match.
    """
    password = click.prompt("Password", hide_input=True)

    if confirm:
        confirm_password = click.prompt("Confirm password", hide_input=True)

        if password != confirm_password:
            raise InvalidPasswordError("Passwords don't match!")

    return password


@click.group()
@click.version_option()
@click.option(
    "-v",
    "--verbosity",
    required=False,
    count=True,
    help="Increase output verbosity",
)
def cli(verbosity: int):
    setup_logger(verbosity)


@cli.command()
def about():
    click.echo(art.text2art(PROJECT_NAME) + ABOUT_PROJECT)


@cli.command()
@click.argument("image_path")
@click.option(
    "-m",
    "--message",
    required=False,
    help="Message to hide into the image.",
)
@click.option(
    "-mp",
    "--message-path",
    required=False,
    help="Path of .txt file for the message to hide into the image.",
)
@click.option(
    "-op",
    "--output-path",
    required=False,
    default=DEFAULT_OUTPUT_DIR,
    show_default="current path",
    help="Output folder to save the modified image.",
)
@click.option(
    "-in",
    "--image-name",
    required=False,
    show_default=f"<original-image>{MODIFIED_IMAGE_SUFFIX}",
    help="Name of the new image file with the hidden message.",
)
@click.option(
    "-c",
    "--compress",
    required=False,
    is_flag=True,
    help="Compress the message before embedding it.",
)
@click.option(
    "-e",
    "--encrypt",
    required=False,
    is_flag=True,
    help="Encrypt the message before embedding it.",
)
def encode(
    image_path: str,
    message: Optional[str],
    message_path: Optional[str],
    output_path: Optional[str],
    image_name: Optional[str],
    compress: bool,
    encrypt: bool,
):
    try:
        logger.info(
            f"Starting message encoding process for image: {image_path}"
        )

        password = None
        if encrypt:
            password = __request_password(confirm=True)

        new_image_path = encode_message(
            image_path=image_path,
            message=message,
            message_path=message_path,
            output_path=output_path,
            image_name=image_name,
            compress=compress,
            password=password,
        )
        click.secho(
            f"Message embedded successfully into {new_image_path}", fg="green"
        )
    except Exception as e:
        click.secho(f"Error: {e}", err=True, fg="red")


@cli.command()
@click.argument("image_path")
@click.option(
    "-op",
    "--output-path",
    required=False,
    default=DEFAULT_OUTPUT_DIR,
    show_default="current path",
    help="Output folder to save the message text.",
)
@click.option(
    "-mn",
    "--message-name",
    required=False,
    show_default=f"<image_name>{MESSAGE_NAME_SUFFIX}",
    help="Name of the message text file to save into the output path.",
)
@click.option(
    "-sm",
    "--save-message",
    required=False,
    is_flag=True,
    help="Save the extracted message into a file into the specified output path.",
)
@click.option(
    "-d",
    "--decrypt",
    required=False,
    is_flag=True,
    help="Decrypt the hidden message.",
)
def decode(
    image_path: str,
    output_path: Optional[str],
    message_name: Optional[str],
    save_message: bool,
    decrypt: bool,
):
    try:
        logger.info(
            f"Starting message decoding process for image: {image_path}"
        )

        password = None
        if decrypt:
            password = __request_password()

        decoded_message = decode_message(
            image_path=image_path,
            output_path=output_path,
            message_name=message_name,
            save_message=save_message,
            password=password,
        )

        if save_message:
            click.secho(
                f"Message saved successfully into {output_path}/{message_name}",
                fg="green",
            )
        else:
            click.secho(
                f"Message decoded successfully: \n{decoded_message}",
                fg="green",
            )
    except Exception as e:
        click.secho(f"Error: {e}", err=True, fg="red")
