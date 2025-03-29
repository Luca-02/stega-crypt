from setuptools import find_packages, setup

from __version__ import VERSION

setup(
    name="stega-crypt",
    version=VERSION,
    description="",
    author="Luca Milanesi",
    author_email="milanesiluca2002@gmail.com",
    url="https://github.com/Luca-02/stega-crypt",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    license="Apache License 2.0",
)
