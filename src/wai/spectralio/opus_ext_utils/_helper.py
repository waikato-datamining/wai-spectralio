from ..serialisation.serialisers import FloatSerialiser, IntSerialiser, NullTerminatedStringSerialiser

# Serialisers
_double_serialiser = FloatSerialiser()
_float_serialiser = FloatSerialiser(double_precision=False)
_int_serialiser = IntSerialiser(signed=False)
_text_serialiser = NullTerminatedStringSerialiser("ascii")


def get_byte(buffer: bytes, offset: int) -> int:
    """
    Gets the byte at the given offset.

    :param buffer:  The buffer to get from.
    :param offset:  The offset from the start of the buffer.
    :return:        The byte value.
    """
    return buffer[offset]


def get_int(buffer: bytes, offset: int) -> int:
    """
    Returns an int at the specified offset.

    :param buffer:  The buffer to get from.
    :param offset:  The offset to use.
    :return:        The int
    """
    return _int_serialiser.deserialise_from_bytes(buffer[offset:offset + 4])


def get_float(buffer: bytes, offset: int) -> float:
    """
    Returns a float at the specified offset.

    :param buffer:  The buffer to get from.
    :param offset:  The offset to use.
    :return:        The float.
    """
    return _float_serialiser.deserialise_from_bytes(buffer[offset:offset + 4])


def get_double(buffer: bytes, offset: int) -> float:
    """
    Returns a double at the specified offset.

    :param buffer:  The buffer to get from.
    :param offset:  The offset to use.
    :return:        The double.
    """
    return _double_serialiser.deserialise_from_bytes(buffer[offset:offset + 8])


def get_text(buffer: bytes, offset: int) -> str:
    """
    Gets text at the given offset.

    :param buffer:  The buffer to get from.
    :param offset:  The offset to use.
    :return:        The text.
    """
    return _text_serialiser.deserialise_from_bytes(buffer[offset:])


def to_hex_string(i: int) -> str:
    """
    Returns the given integer as an unsigned hex representation.

    :param i:   The integer.
    :return:    The hex-string.
    """
    # Check for non-negative integers only
    if i < 0:
        raise ValueError(f"{to_hex_string.__qualname__} only takes non-negative integers, "
                         f"not {i}")

    # Work out how many bytes need representing
    # (plus 1 for safety)
    num_bytes = i.bit_length() // 8 + 1

    # Get the hex-string
    hex_string = i.to_bytes(num_bytes, "big", signed=False).hex()

    # Remove leading zeroes
    while len(hex_string) > 1 and hex_string.startswith("0"):
        hex_string = hex_string[1:]

    return hex_string
