from typing import IO

from ...serialisation import Serialiser
from ...serialisation.serialisers import FloatSerialiser
from .._DataBlock import DataBlock


class DataBlockSerialiser(Serialiser[DataBlock]):
    """
    Serialiser of data-blocks.
    """
    def __init__(self,
                 count: int):
        if count < 1:
            raise ValueError(f"count must be at least one (was {count})")

        self._float_serialiser: FloatSerialiser = FloatSerialiser(double_precision=False)
        self._count: int = count

    def _check(self, obj: DataBlock):
        # Make sure the object really is a data block object.
        if not isinstance(obj, DataBlock):
            raise TypeError("obj is not a DataBlock")

        # Make sure the length matches the provided count
        if len(obj.amplitudes) != self._count:
            raise ValueError(f"Number of amplitudes in data-block does not match count value")

    def _padding_length(self) -> int:
        """
        Gets the number of padding bytes required.

        :return: The number of padding bytes required.
        """
        return ((32 - self._count % 32) % 32) * 4

    def _serialise(self, obj: DataBlock, stream: IO[bytes]):
        # Serialise the amplitudes
        for amplitude in obj.amplitudes:
            self._float_serialiser.serialise(amplitude, stream)

        # Add padding up to 32-byte boundary
        padding = self._padding_length()
        if padding != 0:
            stream.write(b'\x00' * padding)

    def _deserialise(self, stream: IO[bytes]) -> DataBlock:
        db = DataBlock()

        # Read the amplitudes
        for i in range(self._count):
            db.amplitudes.append(self._float_serialiser.deserialise(stream))

        # Consume any padding bytes
        padding = self._padding_length()
        if padding != 0:
            stream.read(padding)

        return db
