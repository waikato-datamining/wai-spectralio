from abc import ABC, abstractmethod
from typing import IO

from .._Serialiser import Serialiser

# The null terminator byte
NULL_BYTE: bytes = b'\x00'


class StringSerialiser(Serialiser[str], ABC):
    """
    Base class for string serialisers.
    """
    def __init__(self, encoding: str = "utf-8"):
        self._encoding: str = encoding

    def _check(self, obj: str):
        # Make sure it really is a string
        if not isinstance(obj, str):
            raise TypeError(f"StringSerialiser serialises strings, got {type(obj)}")

    @abstractmethod
    def _check_encoded(self, encoded: bytes):
        """
        Checks the encoded string is suitable for this serialiser.

        :param encoded:     The encoded string.
        """
        pass

    def _serialise(self, obj: str, stream: IO[bytes]):
        # Encode the string
        encoded: bytes = obj.encode(self._encoding)

        # Check the encoded string
        self._check_encoded(encoded)

        # Serialise the encoded string
        self._serialise_encoded(encoded, stream)

    @abstractmethod
    def _serialise_encoded(self, encoded: bytes, stream: IO[bytes]):
        """
        Serialises the encoded string to the byte-stream.

        :param encoded:     The encoded string.
        :param stream:      The stream.
        """
        pass

    def _deserialise(self, stream: IO[bytes]) -> str:
        return self._deserialise_encoded(stream).decode(self._encoding)

    @abstractmethod
    def _deserialise_encoded(self, stream: IO[bytes]) -> bytes:
        """
        Deserialises the encoded string from the stream.

        :param stream:  The stream.
        :return:        The encoded string.
        """
        pass
