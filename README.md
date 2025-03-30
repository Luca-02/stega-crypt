# stega-crypt

![PyPI](https://img.shields.io/pypi/v/stega-crypt)
![License](https://img.shields.io/github/license/Luca-02/stega-crypt)
![Build Status](https://img.shields.io/github/actions/workflow/status/Luca-02/stega-crypt/build.yaml)
![Coverage](https://img.shields.io/codecov/c/github/Luca-02/stega-crypt)

A steganography tool for securely hiding messages within images.

## Overview

This tool combines steganography and cryptography to provide a secure way to hide sensitive messages within image files. Using the Least Significant Bit (LSB) technique, it embeds data in image pixels with minimal visual impact, while offering optional encryption and compression.

## Features

- **Message Hiding**: Embed text messages inside image files using LSB steganography
- **Message Extraction**: Extract hidden messages from modified images
- **AES Encryption**: Optional AES-GCM encryption on the hidden message for enhanced security
- **Data Compression**: Automatic compression when beneficial
- **CLI Interface**: Easy-to-use command-line interface
- **Noise Addition**: Random noise addition to unused bits for better security

## Installation

Install Stega-Crypt directly from PyPI:

```bash
pip install stega-crypt
```

## Usage

stega-crypt provides a simple command-line interface with the following commands:

### Get Information About the Tool

```bash
stega-crypt about
```

### Hide a Message in an Image

```bash
# Hide a direct message
stega-crypt encode image.png --message "This is a secret message"

# Hide a message from a text file
stega-crypt encode image.png --message-path secret.txt

# Hide a message with compression
stega-crypt encode image.png --message "Secret message" --compress

# Hide a message with encryption
stega-crypt encode image.png --message "Secret message" --encrypt

# Hide a message with custom output path and filename
stega-crypt encode image.png --message "Secret message" --output-path /path/to/folder --image-name image-secret
```

### Extract a Message from an Image

```bash
# Extract and display a message
stega-crypt decode image-secret.png

# Extract a message and save to file
stega-crypt decode image-secret.png --save-message

# Extract an encrypted message
stega-crypt decode image-secret.png --decrypt

# Extract a message with custom output path and filename
stega-crypt decode image-secret.png --save-message --output-path /path/to/folder --message-name extracted
```

### Verbosity Options

You can increase output verbosity using the `-v` or `--verbosity` option:

```bash
stega-crypt -v encode image.png --message "Secret message"  # Informational messages
stega-crypt -vv encode image.png --message "Secret message"  # Debug messages
```

## How It Works

1. **Encoding Process**:
   - If compression is requested, the message is optionally compressed if it reduces size
   - If encryption is requested, the message is encrypted using AES-GCM with a password-derived key
   - The message is converted to binary and embedded in the least significant bits of image pixels
   - Random noise is added to unused LSBs to make detection more difficult
   - The modified image is saved to the specified location

2. **Decoding Process**:
   - The LSB of each pixel is extracted from the image
   - The binary message is rebuilt and converted back to text
   - If compression was used, the message is decompressed
   - If encryption was used, the message is decrypted using the provided password
   - The message is displayed or saved to a file

## Security Features

- **AES-GCM Encryption**: Military-grade encryption with authentication
- **PBKDF2 Key Derivation**: Secure password-to-key derivation with salt
- **LSB Steganography**: Visually imperceptible changes to the image
- **Random Noise**: Addition of random bit flipping in unused LSBs to deter statistical analysis
- **Data Compression**: Optional compression to reduce the steganographic footprint

## Requirements

- [Python](https://www.python.org/downloads/) 3.10+

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
