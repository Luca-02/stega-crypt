import click

from src.steganography.encoder import encode_message


@click.group()
def cli():
    pass


@cli.command()
@click.argument("image_path")
@click.option(
    "-m", "--message", required=False, help="Message to hide into the image."
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
@click.password_option()
# @click.option(
#     '-e', '--encrypt',
#     required=False, is_flag=True,
#     help='Encrypt the message before embedding it.'
# )
# @click.option(
#     '-p', '--password',
#     prompt=True, hide_input=True, confirmation_prompt=False,
#     help='Password to encrypt the hidden message.'
# )
# TODO add verbosity, add a logger to all functionalities
def encode(
    image_path: str,
    message: str,
    message_path: str,
    output_path: str,
    image_name: str,
    compress: bool,
    password: str,
):
    try:
        new_image_path = encode_message(
            image_path=image_path,
            message=message,
            message_path=message_path,
            output_path=output_path,
            image_name=image_name,
            password=password,
            compress=compress,
        )
        click.echo(f"Message embedded successfully into {new_image_path}")
    except Exception as e:
        click.echo(f"Error! {e}")


if __name__ == "__main__":
    cli()
