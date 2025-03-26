import click

from src.config import DEFAULT_OUTPUT_DIR
from src.exceptions import InvalidPasswordError
from src.logger import setup_logger
from src.steganography.encoder import encode_message


@click.group()
def cli():
    pass


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
    "-o",
    "--output-path",
    required=False,
    default=DEFAULT_OUTPUT_DIR,
    show_default="current path",
    help="Output folder to save the modified image.",
)
@click.option(
    "-i",
    "--image-name",
    required=False,
    show_default="<original-image>-modified",
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
@click.option(
    "-v",
    "--verbosity",
    required=False,
    count=True,
    help="Increase output verbosity",
)
def encode(
    image_path: str,
    message: str,
    message_path: str,
    output_path: str,
    image_name: str,
    compress: bool,
    encrypt: bool,
    verbosity,
):
    logger = setup_logger(verbosity)

    try:
        logger.info(
            f"Starting message encoding process for image: {image_path}"
        )

        password = None
        if encrypt:
            logger.info("Encryption requested, prompting for password.")
            password = click.prompt("Password", hide_input=True)
            confirm_password = click.prompt(
                "Confirm password", hide_input=True
            )

            if password != confirm_password:
                raise InvalidPasswordError("Passwords don't match!")

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
