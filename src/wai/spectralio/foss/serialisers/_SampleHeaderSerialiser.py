from typing import IO

from ...serialisation import Serialiser
from ...serialisation.serialisers import IntSerialiser, BoolSerialiser, \
    SecondsSinceEpochSerialiser
from .._SampleHeader import SampleHeader
from ._DateSerialiser import DateSerialiser
from ._SafeStringSerialiser import SafeStringSerialiser


class SampleHeaderSerialiser(Serialiser[SampleHeader]):
    """
    Serialiser of sample headers.
    """
    def __init__(self):
        self._sample_no_serialiser: SafeStringSerialiser = SafeStringSerialiser(13)
        self._client_serialiser: SafeStringSerialiser = SafeStringSerialiser(9)
        self._sample_id_1_serialiser: SafeStringSerialiser = SafeStringSerialiser(50)
        self._sample_id_2_serialiser: SafeStringSerialiser = SafeStringSerialiser(50)
        self._sample_id_3_serialiser: SafeStringSerialiser = SafeStringSerialiser(51, True)
        self._operator_serialiser: SafeStringSerialiser = SafeStringSerialiser(32)
        self._int_serialiser: IntSerialiser = IntSerialiser(num_bytes=2, signed=False)
        self._bool_serialiser: BoolSerialiser = BoolSerialiser()
        self._date_serialiser: DateSerialiser = DateSerialiser()
        self._time_serialiser: SecondsSinceEpochSerialiser = SecondsSinceEpochSerialiser(
            int_serialiser=IntSerialiser(signed=False)
        )

    def _check(self, obj: SampleHeader):
        # Make sure the object really is a sample header object.
        if not isinstance(obj, SampleHeader):
            raise TypeError("obj is not a SampleHeader")

    def _serialise(self, obj: SampleHeader, stream: IO[bytes]):
        self._sample_no_serialiser.serialise(obj.sample_no, stream)
        self._int_serialiser.serialise(obj.sequence, stream)
        self._bool_serialiser.serialise(obj.deleted, stream)
        self._date_serialiser.serialise(obj.date, stream)
        self._int_serialiser.serialise(obj.product_code, stream)
        self._client_serialiser.serialise(obj.client, stream)
        self._sample_id_1_serialiser.serialise(obj.sample_id_1, stream)
        self._sample_id_2_serialiser.serialise(obj.sample_id_2, stream)
        self._sample_id_3_serialiser.serialise(obj.sample_id_3, stream)
        self._operator_serialiser.serialise(obj.operator, stream)
        self._int_serialiser.serialise(obj.standardised, stream)
        self._time_serialiser.serialise(obj.time, stream)

        # Pad
        stream.write(b'\x00' * 38)

    def _deserialise(self, stream: IO[bytes]) -> SampleHeader:
        sh = SampleHeader()

        sh.sample_no = self._sample_no_serialiser.deserialise(stream)
        sh.sequence = self._int_serialiser.deserialise(stream)
        sh.deleted = self._bool_serialiser.deserialise(stream)
        sh.date = self._date_serialiser.deserialise(stream)
        sh.product_code = self._int_serialiser.deserialise(stream)
        sh.client = self._client_serialiser.deserialise(stream)
        sh.sample_id_1 = self._sample_id_1_serialiser.deserialise(stream)
        sh.sample_id_2 = self._sample_id_2_serialiser.deserialise(stream)
        sh.sample_id_3 = self._sample_id_3_serialiser.deserialise(stream)
        sh.operator = self._operator_serialiser.deserialise(stream)
        sh.standardised = self._int_serialiser.deserialise(stream)
        sh.time = self._time_serialiser.deserialise(stream)

        # Consume padding
        stream.read(38)

        return sh
