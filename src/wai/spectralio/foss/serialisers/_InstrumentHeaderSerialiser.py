from typing import IO

from ...serialisation import Serialiser
from ...serialisation.serialisers import IntSerialiser, FloatSerialiser
from .._InstrumentHeader import InstrumentHeader, InstrumentType
from ._SafeStringSerialiser import SafeStringSerialiser


class InstrumentHeaderSerialiser(Serialiser[InstrumentHeader]):
    """
    Serialises an instrument header.
    """
    def __init__(self):
        self._int_serialiser: IntSerialiser = IntSerialiser(num_bytes=2, signed=False)
        self._float_serialiser: FloatSerialiser = FloatSerialiser(double_precision=False)
        self._model_serialiser: SafeStringSerialiser = SafeStringSerialiser(21)
        self._serial_serialiser: SafeStringSerialiser = SafeStringSerialiser(9)
        self._constituent_serialiser: SafeStringSerialiser = SafeStringSerialiser(16)

    def _check(self, obj: InstrumentHeader):
        # Make sure the object really is a instrument header object.
        if not isinstance(obj, InstrumentHeader):
            raise TypeError("obj is not a InstrumentHeader")

    def _serialise(self, obj: InstrumentHeader, stream: IO[bytes]):
        self._int_serialiser.serialise(obj.instrument_type.code, stream)
        self._model_serialiser.serialise(obj.model, stream)
        self._serial_serialiser.serialise(obj.serial, stream)
        self._int_serialiser.serialise(obj.num_seg, stream)
        for i in range(20):
            self._int_serialiser.serialise(obj.points_per_segment[i], stream)
        self._int_serialiser.serialise(obj.spacing_mode, stream)
        for i in range(21):
            self._float_serialiser.serialise(obj.wave[i], stream)
        self._int_serialiser.serialise(obj.neoc, stream)
        stream.write(b'\x00' * 94)
        for i in range(32):
            self._constituent_serialiser.serialise(obj.constituents[i], stream)

    def _deserialise(self, stream: IO[bytes]) -> InstrumentHeader:
        ih = InstrumentHeader()

        ih.instrument_type = InstrumentType.from_code(self._int_serialiser.deserialise(stream))
        ih.model = self._model_serialiser.deserialise(stream)
        ih.serial = self._serial_serialiser.deserialise(stream)
        ih.num_seg = self._int_serialiser.deserialise(stream)
        for i in range(20):
            ih.points_per_segment.append(self._int_serialiser.deserialise(stream))
        ih.spacing_mode = self._int_serialiser.deserialise(stream)
        for i in range(21):
            ih.wave.append(self._float_serialiser.deserialise(stream))
        ih.neoc = self._int_serialiser.deserialise(stream)
        stream.read(94)
        for i in range(32):
            ih.constituents.append(self._constituent_serialiser.deserialise(stream))

        return ih
