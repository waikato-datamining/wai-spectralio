from typing import IO

from .._Serialiser import Serialiser


class BoolSerialiser(Serialiser[bool]):
    """
    Serialiser which serialises a boolean value to a single byte,
    with 0x00 representing False and 0x01 representing True.
    """
    def __init__(self,
                 true_byte: bytes = b'\x01',
                 false_byte: bytes = b'\x00'):
        # Make sure the true and false bytes are 1-byte long
        if len(true_byte) != 1 or len(false_byte) != 1:
            raise ValueError(f"true_byte and false_byte must be single-byte values")

        # Make sure true and false aren't the same
        if true_byte == false_byte:
            raise ValueError(f"true_byte and false_byte are indistinguishable")

        self._true_byte = true_byte
        self._false_byte = false_byte

    def _check(self, obj: bool):
        # Make sure we got a tuple of bools
        if not isinstance(obj, bool):
            raise TypeError(f"{BoolSerialiser.__name__} serialises bools, got {type(obj)}")

    def _serialise(self, obj: bool, stream: IO[bytes]):
        stream.write(self._true_byte if obj else self._false_byte)

    def _deserialise(self, stream: IO[bytes]) -> bool:
        byte = stream.read(1)

        if byte == self._true_byte:
            return True
        elif byte == self._false_byte:
            return False
        else:
            raise ValueError(f"Received invalid byte '{byte}'")
