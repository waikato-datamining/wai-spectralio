from typing import IO

from ...serialisation import Serialiser
from .._FossFile import FossFile
from ._GeneralHeaderSerialiser import GeneralHeaderSerialiser
from ._InstrumentHeaderSerialiser import InstrumentHeaderSerialiser
from ._SampleHeaderSerialiser import SampleHeaderSerialiser
from ._DataBlockSerialiser import DataBlockSerialiser
from ._ConstituentValuesSerialiser import ConstituentValuesSerialiser
from ._SampleInfoSerialiser import SampleInfoSerialiser


class FossFileSerialiser(Serialiser[FossFile]):
    """
    Serialiser of FOSS files.
    """
    def __init__(self):
        self._general_header_serialiser: GeneralHeaderSerialiser = GeneralHeaderSerialiser()
        self._instrument_header_serialiser: InstrumentHeaderSerialiser = InstrumentHeaderSerialiser()
        self._sample_header_serialiser: SampleHeaderSerialiser = SampleHeaderSerialiser()
        self._constituent_values_serialiser: ConstituentValuesSerialiser = ConstituentValuesSerialiser()
        self._sample_info_serialiser: SampleInfoSerialiser = SampleInfoSerialiser()

    def _check(self, obj: FossFile):
        # Make sure the object really is a foss file object.
        if not isinstance(obj, FossFile):
            raise TypeError("obj is not a FossFile")

    def _serialise(self, obj: FossFile, stream: IO[bytes]):
        self._general_header_serialiser.serialise(obj.general_header, stream)
        self._instrument_header_serialiser.serialise(obj.instrument_header, stream)
        data_block_serialiser: DataBlockSerialiser = DataBlockSerialiser(
            obj.general_header.num_points
        )
        for sample in obj.samples:
            self._sample_header_serialiser.serialise(sample[0], stream)
            data_block_serialiser.serialise(sample[1], stream)
            self._constituent_values_serialiser.serialise(sample[2], stream)
        for sample in obj.samples:
            self._sample_info_serialiser.serialise(sample[3], stream)

    def _deserialise(self, stream: IO[bytes]) -> FossFile:
        gh = self._general_header_serialiser.deserialise(stream)
        ih = self._instrument_header_serialiser.deserialise(stream)

        shs = []
        dbs = []
        cvs = []
        sis = []

        data_block_serialiser: DataBlockSerialiser = DataBlockSerialiser(
            gh.num_points
        )

        for i in range(gh.count + gh.deleted):
            shs.append(self._sample_header_serialiser.deserialise(stream))
            dbs.append(data_block_serialiser.deserialise(stream))
            cvs.append(self._constituent_values_serialiser.deserialise(stream))

        for i in range(gh.count + gh.deleted):
            sis.append(self._sample_info_serialiser.deserialise(stream))

        return FossFile(gh, ih, list((sh, db, cv, si) for sh, db, cv, si in zip(shs, dbs, cvs, sis)))
