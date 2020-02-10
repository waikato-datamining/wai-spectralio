from enum import Enum
from typing import List


class InstrumentType(Enum):
    SER_4250 = 0
    SER_51A = 1
    SIC_4250 = 2
    SIC_6250 = 3
    SIC_6250V = 4
    PARALLEL_6250 = 5
    PARALLEL_6250V = 6
    BL_500 = 7
    BL_400 = 8
    SIC_6500 = 9
    SIC_5500 = 10
    SIC_5000 = 11
    SIC_4500 = 12
    INFRATEC = 13

    code = property(lambda self: self.value)

    @classmethod
    def from_code(cls, code: int) -> 'InstrumentType':
        """
        Gets an instrument type from its code.

        :param code:    The instrument type code.
        :return:        The instrument type.
        """
        for instrument_type in cls:
            if instrument_type.code == code:
                return instrument_type

        raise ValueError(f"No instrument type with code {code} found")


class InstrumentHeader:
    """
    Instrument Header class.
    """
    def __init__(self):
        # 2 BYTES: Instrument type
        self.instrument_type: InstrumentType = InstrumentType.SER_4250

        # char[21] model number
        self.model: str = ""

        # char[9] serial number
        self.serial: str = ""

        # 2 BYTES integer, number of segments up to 20 (?)
        self.num_seg: int = 0

        # 40 BYTES int[20], points per sement.. ?
        self.points_per_segment: List[int] = []

        # 2 BYTES int spacing mode: 00=TILFIL, 01=EQUALSPC, 02=FILFIL, 03=SIN
        self.spacing_mode: int = 0

        # start float[7], inc float[7], end float[7] but looking at
        self.wave: List[float] = []

        # 2 BYTES int, number of EOC's (??) use 4400?
        self.neoc: int = 0

        # 94 bytes of padding

        # 32 * 16 chars, null terminated constituent names
        self.constituents: List[str] = []

    @property
    def starts(self) -> List[float]:
        return self.wave[0:7]

    @property
    def increments(self) -> List[float]:
        return self.wave[7:14]

    @property
    def ends(self) -> List[float]:
        return self.wave[14:21]
