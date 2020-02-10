from typing import IO

from .._Serialiser import Serialiser
from ._StringSerialiser import StringSerialiser
from ._IntSerialiser import IntSerialiser


class LengthPrefixedStringSerialiser(StringSerialiser):
    """
    Serialiser of strings. Serialises the length of the string
    before serialising the string itself.
    """
    def __init__(self,
                 encoding: str = "utf-8",
                 length_serialiser: Serialiser[int] = IntSerialiser()):
        super().__init__(encoding)

        self._length_serialiser: Serialiser[int] = length_serialiser

    def _check_encoded(self, encoded: bytes):
        # No checks needed
        pass

    def _serialise_encoded(self, encoded: bytes, stream: IO[bytes]):
        # Get the byte-length of the string
        byte_length: int = len(encoded)

        # Serialise the byte length
        self._length_serialiser.serialise(byte_length, stream)

        # Write the string bytes
        stream.write(encoded)

    def _deserialise_encoded(self, stream: IO[bytes]) -> bytes:
        # Read the length from the stream
        byte_length: int = self._length_serialiser.deserialise(stream)

        return stream.read(byte_length)
