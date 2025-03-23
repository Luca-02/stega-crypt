import click

from exceptions import InvalidPasswordError
from src.config import DEFAULT_OUTPUT_DIR
from steganography.encoder import encode_message


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
    type=click.STRING,
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
# TODO add verbosity, add a logger to all functionalities
def encode(
    image_path: str,
    message: str,
    message_path: str,
    output_path: str,
    image_name: str,
    compress: bool,
    encrypt: bool,
):
    try:
        password = None
        if encrypt:
            password = click.prompt("Password: ", hide_input=True)
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
        click.echo(f"Message embedded successfully into {new_image_path}")
    except Exception as e:
        click.secho(f"Error! {e}", err=True, fg="red")


if __name__ == "__main__":
    cli()
