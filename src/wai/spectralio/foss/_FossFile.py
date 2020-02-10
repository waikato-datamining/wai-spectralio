from typing import Tuple, List

from ._GeneralHeader import GeneralHeader
from ._InstrumentHeader import InstrumentHeader
from ._SampleHeader import SampleHeader
from ._DataBlock import DataBlock
from ._ConstituentValues import ConstituentValues
from ._SampleInfo import SampleInfo


class FossFile:
    """
    Class representing a FOSS file.
    """
    def __init__(self,
                 general_header: GeneralHeader,
                 instrument_header: InstrumentHeader,
                 samples: List[Tuple[SampleHeader, DataBlock, ConstituentValues, SampleInfo]]):
        self.general_header: GeneralHeader = general_header
        self.instrument_header: InstrumentHeader = instrument_header
        self.samples: List[Tuple[SampleHeader, DataBlock, ConstituentValues, SampleInfo]] = samples
