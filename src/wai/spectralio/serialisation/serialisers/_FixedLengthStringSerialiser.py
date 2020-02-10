from typing import IO

from ._StringSerialiser import StringSerialiser, NULL_BYTE


class FixedLengthStringSerialiser(StringSerialiser):
    """
    Serialises strings to a fixed length. If the string
    is shorter than the fixed length, it is padded with
    null-bytes. If the string is longer than the fixed
    length, it will be truncated, or raise an exception
    if selected.

    N.B. Be careful using this serialiser with variable
    length encoding schemes, as partial letters may be
    truncated.
    """
    def __init__(self,
                 length: int,
                 encoding: str = "utf-8",
                 ensure_null_terminated: bool = False,
                 raise_on_truncate: bool = False):
        super().__init__(encoding)

        # Make sure length is positive
        if length <= 0:
            raise ValueError(f"Length must be a positive value, not {length}")

        self._length: int = length - 1 if ensure_null_terminated else length
        self._ensure_null_terminated: bool = ensure_null_terminated
        self._raise_on_truncate: bool = raise_on_truncate

    def _check_encoded(self, encoded: bytes):
        # Check for truncation
        if self._raise_on_truncate:
            if len(encoded) > self._length:
                raise ValueError(f"Encoded string of length {len(encoded)} will truncate")

    def _serialise_encoded(self, encoded: bytes, stream: IO[bytes]):
        # Write the (possibly truncated) string bytes
        stream.write(encoded[:self._length])

        # Pad to length with null-bytes as necessary
        if len(encoded) < self._length:
            stream.write(NULL_BYTE * (self._length - len(encoded)))

        # Write the null terminator if selected
        if self._ensure_null_terminated:
            stream.write(NULL_BYTE)

    def _deserialise_encoded(self, stream: IO[bytes]) -> bytes:
        # Read the encoded string
        encoded = stream.read(self._length)

        # Remove any padding
        while encoded.endswith(NULL_BYTE):
            encoded = encoded[:-1]

        # Consume the null-terminator if expected
        if self._ensure_null_terminated:
            stream.read(1)

        return encoded
