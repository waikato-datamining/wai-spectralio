from typing import List

from .api import Spectrum
from .foss import *
from .nir import Writer as NIRWriter, Reader as NIRReader
from .options import Option


class Reader(NIRReader):
    """
    Reads spectra from .CAL file.

    Identical to NIR reader.
    """
    pass


class Writer(NIRWriter):
    """
    Write spectra to .CAL file.
    As per .NIR file, except with 'constituent values'. i.e. reference values.
    """
    # Options
    constituents = Option(help="constituents (modeling targets)", default=[], nargs='+')

    def get_general_header(self, data: List[Spectrum]) -> GeneralHeader:
        gh = super().get_general_header(data)
        gh.type = 2
        gh.num_consts = len(self.constituents)
        return gh

    def get_instrument_header(self) -> InstrumentHeader:
        ih = super().get_instrument_header()

        ih.constituents = self.constituents

        return ih

    def get_constituent_values(self, sp: Spectrum) -> ConstituentValues:
        cv = ConstituentValues()

        sampledata = sp.sample_data
        if sampledata is None:
            return cv

        for constituent in self.constituents:
            cv.constituents.append(float(sampledata[constituent])
                                   if constituent in sampledata
                                   else 0.0)

        return cv


read = Reader.read


write = Writer.write
