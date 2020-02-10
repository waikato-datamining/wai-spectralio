from typing import IO

from ...serialisation.serialisers import FixedLengthStringSerialiser, NULL_BYTE


class SafeStringSerialiser(FixedLengthStringSerialiser):
    """
    Serialiser which serialises strings to ASCII, discarding any
    unsafe characters. Also ignores characters after the first
    null-byte.
    """
    def __init__(self,
                 length: int,
                 ensure_null_terminated: bool = False):
        super().__init__(length, "ascii", ensure_null_terminated)

    def _deserialise_encoded(self, stream: IO[bytes]) -> bytes:
        encoded = super()._deserialise_encoded(stream)

        # Remove any characters after the first null-byte
        if NULL_BYTE in encoded:
            encoded = encoded[:encoded.index(NULL_BYTE)]

        return bytes(b for b in encoded if b < 0x80)
