from typing import IO

from .._Serialiser import Serialiser

# The null terminator byte
NULL_BYTE: bytes = b'\x00'


class NullTerminatedStringSerialiser(Serialiser[str]):
    """
    Serialiser of strings. Encodes the string with a given encoding
    and appends a null terminator to the end. If specified, the string
    is padded with null terminators up to a given length.
    """
    def __init__(self,
                 encoding: str = "utf-8",
                 fixed_length: int = 0,
                 fixed_length_ignore_null: bool = False):
        self._encoding: str = encoding
        self._fixed_length: int = fixed_length
        self._fixed_length_ignore_null: bool = fixed_length_ignore_null

    def _check(self, obj: str):
        # Make sure it really is a string
        if not isinstance(obj, str):
            raise TypeError(f"StringSerialiser serialises strings, got {type(obj)}")

    def _serialise(self, obj: str, stream: IO[bytes]):
        # Encode the string
        byte_string = obj.encode()

        # Pad/truncate to the fixed length, if provided
        if self._fixed_length > 0:
            if len(byte_string) < self._fixed_length:
                byte_string += NULL_BYTE * (self._fixed_length - len(byte_string))
            else:
                byte_string = byte_string[:self._fixed_length]

        # Add the terminator byte unless set to ignore
        if self._fixed_length > 0:
            if not self._fixed_length_ignore_null:
                byte_string = byte_string[:-1] + NULL_BYTE
        else:
            byte_string = byte_string + NULL_BYTE

        stream.write(byte_string)

    def _deserialise(self, stream: IO[bytes]) -> str:
        # Read the bytes
        byte_string: bytes = b''
        if self._fixed_length > 0:
            byte_string = stream.read(self._fixed_length)
        else:
            while not byte_string.endswith(NULL_BYTE):
                byte_string += stream.read(1)

        # Remove any null bytes
        while byte_string.endswith(NULL_BYTE):
            byte_string = byte_string[:-1]

        return byte_string.decode(self._encoding)
