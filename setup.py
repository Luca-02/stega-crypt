from pathlib import Path

from setuptools import find_packages, setup

from src.config import AUTHOR, PROJECT_NAME, PROJECT_URL

this_directory = Path(__file__).parent

with open(this_directory / "requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name=PROJECT_NAME,
    version=(this_directory / "VERSION").read_text(),
    description="A steganography library with cryptography for hiding messages in images.",
    long_description=(this_directory / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email="milanesiluca2002@gmail.com",
    url=PROJECT_URL,
    project_urls={"Source Code": PROJECT_URL},
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    license="Apache License 2.0",
    install_requires=required,
    entry_points={
        "console_scripts": ["stega-crypt = src.cli:cli"],
    },
)
