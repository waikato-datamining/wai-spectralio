from typing import IO

from .._Serialiser import Serialiser


class IntSerialiser(Serialiser[int]):
    def __init__(self,
                 little_endian: bool = True,
                 num_bytes: int = 4,
                 signed: bool = True):
        # Make sure num_bytes is a positive value
        if num_bytes < 1:
            raise ValueError(f"num_bytes must be at least 1")

        self._endianness: str = "little" if little_endian else "big"
        self._num_bytes: int = num_bytes
        self._signed: bool = signed

    def _check(self, obj: int):
        # Make sure the value really is an int
        if not isinstance(obj, int):
            raise TypeError(f"IntSerialiser expects ints, got {type(obj)}")

        # Make sure it is positive if we're in unsigned mode
        if not self._signed and obj < 0:
            raise ValueError(f"Can't serialise negative ints in unsigned mode")

        # Make sure the value is not too big
        if self.bit_length_actual(obj, self._signed) > 8 * self._num_bytes:
            raise ValueError(f"Int magnitude is too big for current num_bytes setting "
                             f"({obj} won't fit in {self._num_bytes} "
                             f"byte{'s' if self._num_bytes > 1 else ''})")

    @staticmethod
    def bit_length_actual(value: int, signed: bool) -> int:
        """
        Gets the actual bit-length of the serialised int,
        taking into account the sign-mode of the serialiser.

        :param value:   The int to serialise.
        :param signed:  Whether the bit-representation is signed.
        :return:        The serialised bit-length.
        """
        # Zero always takes 1 bit
        if value == 0:
            return 1

        # Positive value, signed field
        if signed and value > 0:
            return value.bit_length() + 1

        # Negative value, signed field
        if signed and value < 0:
            return (value + 1).bit_length() + 1

        # Positive value, unsigned field
        if value > 0:
            return value.bit_length()

        # Negative value, unsigned field
        raise ValueError(f"Can't find unsigned bit-length of signed value {value}")

    def _serialise(self, obj: int, stream: IO[bytes]):
        stream.write(obj.to_bytes(self._num_bytes, self._endianness, signed=self._signed))

    def _deserialise(self, stream: IO[bytes]) -> int:
        bytes_ = stream.read(self._num_bytes)
        return int.from_bytes(bytes_, self._endianness, signed=self._signed)
