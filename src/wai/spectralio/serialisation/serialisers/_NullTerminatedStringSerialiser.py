from typing import IO

from ._StringSerialiser import StringSerialiser, NULL_BYTE


class NullTerminatedStringSerialiser(StringSerialiser):
    """
    Serialises a string by appending a null byte after the
    encoded string.
    """
    def __init__(self,
                 encoding: str = "utf-8"):
        super().__init__(encoding)

    def _check_encoded(self, encoded: bytes):
        # Check the encoded string doesn't already contain null-bytes
        if NULL_BYTE in encoded:
            raise ValueError(f"Encoded string {encoded} contains a null-byte")

    def _serialise_encoded(self, encoded: bytes, stream: IO[bytes]):
        stream.write(encoded)
        stream.write(NULL_BYTE)

    def _deserialise_encoded(self, stream: IO[bytes]) -> bytes:
        # Read the bytes
        byte_string: bytes = b''
        while not byte_string.endswith(NULL_BYTE):
            byte_string += stream.read(1)

        # Return without the null-byte
        return byte_string[:-1]
