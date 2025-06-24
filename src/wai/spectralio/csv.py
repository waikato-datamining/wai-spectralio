import csv
import locale
import re
from typing import Type

from simple_range import Index, Range

from .api import SpectrumReader, SpectrumWriter, Spectrum
from .mixins import LocaleOptionsMixin
from .options import Option
from .util import with_locale

PH_WAVE_NUMBER = "{WAVE}"
PH_INDEX = "{INDEX}"
PLACEHOLDERS = [
    PH_WAVE_NUMBER,
    PH_INDEX,
]


class Reader(LocaleOptionsMixin, SpectrumReader):
    """
    Reads spectra in CSV format (row-wise).
    """
    # Options
    sample_id = Option(help='the column with the sample id (1-based index)', default='1')
    spectral_data = Option(help='the columns with the spectral data (range, using 1-based indices)', default='2-last')
    sample_data = Option(help='the optional column(s) with sample data values (range, using 1-based indices)', default=None)
    sample_data_prefix = Option(help='The prefix used in the columns with the sample data', default=None)
    delimiter = Option(help='the column separator to use', default=',')
    wave_numbers_in_header = Option(help='Whether the wave numbers are encoded in the column headers', action='store_true')
    wave_numbers_regexp = Option(help='The regular expression for extracting the wave numbers from the column headers (1st group is used)', default='(.*)')

    def _read_locale_unaware(self, spec_file, filename):
        """
        Reads the spectra from the file handle.

        :param spec_file:   The file handle to read from.
        :param filename:    The file being read.
        :return:            A list of spectra in the file.
        """
        result = []
        reader = csv.reader(spec_file, delimiter=self.delimiter)
        first = True
        sample_id_index = None
        spectral_data_range = None
        sample_data_range = None
        sample_data_names = None
        wave_numbers = []
        for row in reader:
            if first:
                first = False
                sample_id_index = Index(self.sample_id, maximum=len(row)).value()
                spectral_data_range = Range(self.spectral_data, maximum=len(row)).indices()
                if self.sample_data is not None:
                    sample_data_range = Range(self.sample_data, maximum=len(row)).indices()
                    sample_data_names = [row[x] for x in sample_data_range]
                    if self.sample_data_prefix is not None:
                        for i, name in enumerate(sample_data_names):
                            if name.startswith(self.sample_data_prefix):
                                sample_data_names[i] = name[len(self.sample_data_prefix):]
                if self.wave_numbers_in_header:
                    for i in spectral_data_range:
                        match = re.match(self.wave_numbers_regexp, str(row[i]))
                        if match is None:
                            wave_numbers.append(i)
                        else:
                            wave_numbers.append(locale.atof(match.group(1)))
                else:
                    wave_numbers = [x for x in range(len(spectral_data_range))]
            else:
                sample_id = row[sample_id_index]
                amplitudes = [locale.atof(row[x]) for x in spectral_data_range]
                sample_data = dict()
                if sample_data_range is not None:
                    for i, r in enumerate(sample_data_range):
                        sample_data[sample_data_names[i]] = row[r]
                result.append(Spectrum(sample_id, wave_numbers[:], amplitudes, sample_data))

        return result

    def _read(self, spec_file, filename):
        """
        Reads the spectra from the file handle.

        :param spec_file:   The file handle to read from.
        :param filename:    The file being read.
        :return:            A list of spectra in the file.
        """
        return with_locale(self.locale)(self._read_locale_unaware)(spec_file, filename)

    def binary_mode(self, filename: str) -> bool:
        """
        Whether the file should be accessed in binary mode.

        :param filename:    The name of the file.
        :return:            True if it should be accessed in binary mode,
                            False if not.
        """
        return False

    @classmethod
    def get_writer_class(cls) -> 'Type[Writer]':
        """
        Gets the writer class that writes the same file-type as
        this reader class reads.

        :return:    The writer.
        """
        return Writer


class Writer(LocaleOptionsMixin, SpectrumWriter):
    """
    Writer that stores spectra in CSV format (row-wise).
    """
    # Options
    sample_id = Option(help='The column header to use for the sample ID column', default='sample_id')
    sample_data = Option(help='The names of the sample data values to output', default=None, nargs='*')
    sample_data_prefix = Option(help='The prefix to use for the sample data headers', default='')
    wave_numbers_format = Option(help='The format to use for the wave number headers, the following placeholders are available: ' + "|".join(PLACEHOLDERS), default=PH_WAVE_NUMBER)
    delimiter = Option(help='the column separator to use', default=',')

    def _write_locale_unaware(self, spectra, spec_file, as_bytes):
        """
        Writes the spectra to the filehandle.

        :param spectra: the list of spectra
        :type spectra: list
        :param spec_file: the file handle to use
        :type spec_file: file
        :param as_bytes: whether to write as bytes or string
        :type as_bytes: bool
        """
        writer = csv.writer(spec_file, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)

        # ensure that all spectra have same number wave numbers
        if len(spectra) > 1:
            for i in range(1, len(spectra)):
                if len(spectra[0].waves) != len(spectra[1].waves):
                    raise Exception("Number of wave numbers differ (#%d vs #%d): %d != %d" % (0, i, len(spectra[0].waves), len(spectra[1].waves)))

        first = True
        for spectrum in spectra:
            # header
            if first:
                first = False
                row = [self.sample_id]
                for i, w in enumerate(spectrum.waves):
                    col = self.wave_numbers_format
                    col = col.replace(PH_INDEX, str(i))
                    col = col.replace(PH_WAVE_NUMBER, locale.str(w))
                    row.append(col)
                if self.sample_data is not None:
                    for sd in self.sample_data:
                        col = self.sample_data_prefix + sd
                        row.append(col)
                writer.writerow(row)

            # data
            row = [spectrum.id]
            for ampl in spectrum.amplitudes:
                row.append(locale.str(ampl))
            if self.sample_data is not None:
                for sd in self.sample_data:
                    if sd in spectrum.sample_data:
                        row.append(spectrum.sample_data[sd])
                    else:
                        row.append(None)
            writer.writerow(row)

    def _write(self, spectra, spec_file, as_bytes):
        """
        Writes the spectra to the file-handle.

        :param spectra:     The list of spectra.
        :param spec_file:    The file handle to write to.
        :param as_bytes:    Whether to write as bytes or string.
        """
        with_locale(self.locale)(self._write_locale_unaware)(spectra, spec_file, as_bytes)

    def binary_mode(self, filename: str) -> bool:
        """
        Whether the file should be accessed in binary mode.

        :param filename:    The name of the file.
        :return:            True if it should be accessed in binary mode,
                            False if not.
        """
        return False

    @classmethod
    def get_reader_class(cls) -> Type[Reader]:
        """
        Gets the reader class that reads the same file-type as
        this writer class writes.

        :return:    The reader class.
        """
        return Reader


read = Reader.read
write = Writer.write
