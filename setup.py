from setuptools import setup, find_packages

setup(
    name='stega-crypt',
    version='0.1',
    description='',
    author='Luca Milanesi',
    author_email='milanesiluca2002@gmail.com',
    url='https://github.com/Luca-02/stega-crypt',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    license='Apache License 2.0'
)
