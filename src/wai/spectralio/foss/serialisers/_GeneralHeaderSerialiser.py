from typing import IO

from ...serialisation import Serialiser
from ...serialisation.serialisers import (
    IntSerialiser,
    SecondsSinceEpochSerialiser
)
from .._GeneralHeader import GeneralHeader
from ._DateSerialiser import DateSerialiser
from ._SafeStringSerialiser import SafeStringSerialiser


class GeneralHeaderSerialiser(Serialiser[GeneralHeader]):
    def __init__(self):
        self._int_serialiser: IntSerialiser = IntSerialiser(num_bytes=2, signed=False)
        self._file_id_serialiser: SafeStringSerialiser = SafeStringSerialiser(71)
        self._master_serialiser: SafeStringSerialiser = SafeStringSerialiser(9)
        self._packing_serialiser: SafeStringSerialiser = SafeStringSerialiser(30)
        self._date_serialiser: DateSerialiser = DateSerialiser()
        self._time_serialiser: SecondsSinceEpochSerialiser = SecondsSinceEpochSerialiser(
            int_serialiser=IntSerialiser(signed=False)
        )

    def _check(self, obj: GeneralHeader):
        # Make sure the object really is a general header object.
        if not isinstance(obj, GeneralHeader):
            raise TypeError("obj is not a GeneralHeader")

    def _serialise(self, obj: GeneralHeader, stream: IO[bytes]):
        self._int_serialiser.serialise(obj.type, stream)
        self._int_serialiser.serialise(obj.count, stream)
        self._int_serialiser.serialise(obj.deleted, stream)
        self._int_serialiser.serialise(obj.num_points, stream)
        self._int_serialiser.serialise(obj.num_consts, stream)
        self._date_serialiser.serialise(obj.creation_date, stream)
        self._time_serialiser.serialise(obj.time, stream)
        self._int_serialiser.serialise(obj.most_recent, stream)
        self._file_id_serialiser.serialise(obj.file_id, stream)
        self._master_serialiser.serialise(obj.master, stream)
        self._packing_serialiser.serialise(obj.packing, stream)

    def _deserialise(self, stream: IO[bytes]) -> GeneralHeader:
        gh = GeneralHeader()

        gh.type = self._int_serialiser.deserialise(stream)
        gh.count = self._int_serialiser.deserialise(stream)
        gh.deleted = self._int_serialiser.deserialise(stream)
        gh.num_points = self._int_serialiser.deserialise(stream)
        gh.num_consts = self._int_serialiser.deserialise(stream)
        gh.creation_date = self._date_serialiser.deserialise(stream)
        gh.time = self._time_serialiser.deserialise(stream)
        gh.most_recent = self._int_serialiser.deserialise(stream)
        gh.file_id = self._file_id_serialiser.deserialise( stream)
        gh.master = self._master_serialiser.deserialise(stream)
        gh.packing = self._packing_serialiser.deserialise(stream)

        return gh
