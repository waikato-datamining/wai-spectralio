import struct
from typing import IO

from .._Serialiser import Serialiser


class FloatSerialiser(Serialiser[float]):
    def __init__(self,
                 little_endian: bool = True,
                 double_precision: bool = True):
        self._format = f"{'<' if little_endian else '>'}{'d' if double_precision else 'f'}"
        self._num_bytes: int = 8 if double_precision else 4

    def _check(self, obj: float):
        # Make sure the object really is a float
        if not isinstance(obj, float):
            raise TypeError(f"Received non-float value of type {type(obj).__name__}")

    def _serialise(self, obj: float, stream: IO[bytes]):
        stream.write(struct.pack(self._format, obj))

    def _deserialise(self, stream: IO[bytes]) -> float:
        return struct.unpack(self._format, stream.read(self._num_bytes))[0]
