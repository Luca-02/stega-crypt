def bytes_to_bits_binary_list(byte_data: bytes) -> list[int]:
    """
    Converts a bytes object into a list of binary bits.

    :param byte_data: Bytes object.
    :return: The corresponding list of binary bits.
    """
    return [int(bit) for bit in ''.join(f'{byte:08b}' for byte in byte_data)]
