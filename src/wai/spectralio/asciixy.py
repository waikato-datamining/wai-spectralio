from typing import Type

from .api import Spectrum, SpectrumReader, SpectrumWriter
from .options import Option
from .sampleidextraction import SampleIDExtraction


class Reader(SampleIDExtraction, SpectrumReader):
    """
    Reader for ADAMS spectra.
    """
    # Options
    separator = Option(help='the separator to use for identifying X and Y columns', default=';')

    def _read(self, spec_file, filename):
        """
        Reads the spectra from the file handle.

        :param spec_file: the file handle to read from
        :type spec_file: file
        :param filename: the file being read
        :type filename: str
        :return: the list of spectra
        :rtype: list
        """
        sample_id = self.extract(filename)
        waves = []
        ampls = []
        for line in spec_file.readlines():
            line = line.strip()
            if len(line) == 0:
                continue

            parts = line.split(self.separator)

            waves.append(float(parts[0]))
            ampls.append(float(parts[1]))

        waves.reverse()
        ampls.reverse()

        return [Spectrum(sample_id, waves, ampls)]

    def binary_mode(self, filename: str) -> bool:
        return False

    @classmethod
    def get_writer_class(cls) -> 'Type[Writer]':
        return Writer


class Writer(SpectrumWriter):
    """
    Writer for ADAMS spectra.
    """
    # Options
    separator = Option(help='the separator to use for identifying X and Y columns', default=';')

    def _write(self, spectra, spec_file, as_bytes):
        """
        Writes the spectra to the filehandle.

        :param spectra: the list of spectra
        :type spectra: list
        :param spec_file: the file handle to use
        :type spec_file: file
        """
        if len(spectra) != 1:
            raise ValueError("Can only write a single spectrum")

        spectrum = spectra[0]

        for wave, ampl in reversed(list(zip(spectrum.waves, spectrum.amplitudes))):
            spec_file.write(f"{wave}{self.separator}{ampl}\n")

    def binary_mode(self, filename: str) -> bool:
        return False

    def get_reader_class(cls) -> Type[Reader]:
        return Reader


read = Reader.read


write = Writer.write
