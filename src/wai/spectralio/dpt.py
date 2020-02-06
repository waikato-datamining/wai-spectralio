import locale
import os
import re
from typing import Type, IO, List

from .api import SpectrumReader, SpectrumWriter, Spectrum
from .mixins import LocaleOptionsMixin
from .options import Option
from .util import with_locale


class Reader(LocaleOptionsMixin, SpectrumReader):
    """
    Reads spectra in DPT format.
    """
    def _read(self, spec_file: IO[str], filename: str) -> List[Spectrum]:
        return with_locale(self.locale)(self._read_locale_unaware)(spec_file, filename)

    def _read_locale_unaware(self, spec_file: IO[str], filename: str) -> List[Spectrum]:
        """
        Reads the spectra from the file handle. Assumes the locale
        is already set correctly.

        :param spec_file:   The file handle to read from.
        :param filename:    The file being read.
        :return:            A list of spectra in the file.
        """
        # Create an empty spectrum to hold the parsed data
        sp = Spectrum(os.path.splitext(os.path.basename(filename))[0])

        for line in spec_file:
            vals: List[str] = re.split(r'\s', line.strip())

            if len(vals) != 2:
                self.logger.critical(f"Data line corrupt: '{line}' split into: " +
                                     f"{len(vals)}(" +
                                     ")(".join(vals) +
                                     ")")
                break

            try:
                sp.waves.append(locale.atof(vals[0]))
                sp.amplitudes.append(locale.atof(vals[1]))
            except ValueError:
                self.logger.exception(f"Data line corrupt: '{line}'")
                break

        return [sp]

    @classmethod
    def get_writer_class(cls) -> 'Type[SpectrumWriter]':
        return Writer

    def binary_mode(self, filename: str) -> bool:
        return False


class Writer(LocaleOptionsMixin, SpectrumWriter):
    """
    Writer that stores spectrums in the simple CSV format.
    """
    # Options
    descending = Option(help="output the spectrum in descending x-axis order", action="store_true")

    def _write(self, spectra: List[Spectrum], spec_file: IO[str], as_bytes: bool):
        with_locale(self.locale)(self._write_locale_unaware)(spectra, spec_file, as_bytes)

    def _write_locale_unaware(self, spectra: List[Spectrum], spec_file: IO[str], as_bytes: bool):
        """
        Writes the spectra to the file-handle. Assumes the locale
        is already set correctly.

        :param spectra:     The list of spectra.
        :param spec_file:    The file handle to write to.
        :param as_bytes:    Whether to write as bytes or string.
        """
        # Should only be one spectrum
        if len(spectra) != 1:
            self.logger.warning(f"DPT writer can only write one spectra to a file, "
                                f"got {len(spectra)}")

        for wave, amplitude in zip(spectra[0].waves, spectra[0].amplitudes):
            spec_file.write(f"{locale.str(wave)}\t{locale.str(amplitude)}\n")

    @classmethod
    def get_reader_class(cls) -> Type[SpectrumReader]:
        return Reader

    def binary_mode(self, filename: str) -> bool:
        return False


read = Reader.read


write = Writer.write
