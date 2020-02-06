from typing import IO

from .._Serialiser import Serialiser
from ._IntSerialiser import IntSerialiser


class LengthPrefixedStringSerialiser(Serialiser[str]):
    """
    Serialiser of strings. Encodes the string and serialises
    the string's length and adds it to the beginning.
    """
    def __init__(self,
                 encoding: str = "utf-8",
                 length_serialiser: Serialiser[int] = IntSerialiser()):
        self._encoding: str = encoding
        self._length_serialiser: Serialiser[int] = length_serialiser

    def _check(self, obj: str):
        # Make sure it really is a string
        if not isinstance(obj, str):
            raise TypeError(f"LengthPrefixedStringSerialiser serialises strings, got {type(obj)}")

    def _serialise(self, obj: str, stream: IO[bytes]):
        # Encode the string
        string_bytes = obj.encode(self._encoding)

        # Get the byte-length of the string
        byte_length: int = len(string_bytes)

        # Serialise the byte length
        self._length_serialiser.serialise(byte_length, stream)

        # Write the string bytes
        stream.write(string_bytes)

    def _deserialise(self, stream: IO[bytes]) -> str:
        # Read the length from the stream
        byte_length: int = self._length_serialiser.deserialise(stream)

        # Read the bytes from the stream
        string_bytes: bytes = stream.read(byte_length)

        # Decode and return the string
        return string_bytes.decode(self._encoding)
