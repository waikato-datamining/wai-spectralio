from typing import IO

from ...serialisation import Serialiser
from ...serialisation.serialisers import IntSerialiser, BoolSerialiser
from .._SampleInfo import SampleInfo
from ._SafeStringSerialiser import SafeStringSerialiser


class SampleInfoSerialiser(Serialiser[SampleInfo]):
    """
    Serialiser of sample info.
    """
    def __init__(self):
        self._int_serialiser: IntSerialiser = IntSerialiser(num_bytes=2, signed=False)
        self._bool_serialiser: BoolSerialiser = BoolSerialiser()
        self._sample_id_serialiser: SafeStringSerialiser = SafeStringSerialiser(13)

    def _check(self, obj: SampleInfo):
        # Make sure the object really is a sample info object.
        if not isinstance(obj, SampleInfo):
            raise TypeError("obj is not a SampleInfo")

    def _serialise(self, obj: SampleInfo, stream: IO[bytes]):
        self._sample_id_serialiser.serialise(obj.sample_id, stream)
        self._int_serialiser.serialise(obj.sequence, stream)
        self._bool_serialiser.serialise(obj.deleted, stream)

    def _deserialise(self, stream: IO[bytes]) -> SampleInfo:
        si = SampleInfo()

        si.sample_id = self._sample_id_serialiser.deserialise(stream)
        si.sequence = self._int_serialiser.deserialise(stream)
        si.deleted = self._bool_serialiser.deserialise(stream)

        return si
