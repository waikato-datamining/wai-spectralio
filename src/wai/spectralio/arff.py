import arff
import locale
import re
from typing import Type

from simple_range import Index, Range

from .api import SpectrumReader, SpectrumWriter, Spectrum
from .options import Option

PH_WAVE_NUMBER = "{WAVE}"
PH_INDEX = "{INDEX}"
PLACEHOLDERS = [
    PH_WAVE_NUMBER,
    PH_INDEX,
]


class Reader(SpectrumReader):
    """
    Reads spectra in ARFF format (row-wise).
    """
    # Options
    sample_id = Option(help='the attribute with the sample id (1-based index)', default='1')
    spectral_data = Option(help='the attributes with the spectral data (range, using 1-based indices)', default='2-last')
    sample_data = Option(help='the optional attribute(s) with sample data values (range, using 1-based indices)', default=None)
    sample_data_prefix = Option(help='The prefix in use for the sample data attributes', default=None)
    wave_numbers_in_header = Option(help='Whether the wave numbers are encoded in the attribute name', action='store_true')
    wave_numbers_regexp = Option(help='The regular expression for extracting the wave numbers from the attribute names (1st group is used)', default='(.*)')

    def _read(self, spec_file, filename):
        """
        Reads the spectra from the file handle.

        :param spec_file:   The file handle to read from.
        :param filename:    The file being read.
        :return:            A list of spectra in the file.
        """
        data = arff.load(spec_file)
        sample_data_range = None
        sample_data_names = None
        sample_data_types = None
        wave_numbers = []

        # header
        sample_id_index = Index(self.sample_id, maximum=len(data['attributes'])).value()
        spectral_data_range = Range(self.spectral_data, maximum=len(data['attributes'])).indices()
        if self.sample_data is not None:
            sample_data_range = Range(self.sample_data, maximum=len(data['attributes'])).indices()
            sample_data_names = [data['attributes'][x][0] for x in sample_data_range]
            sample_data_types = [data['attributes'][x][1] for x in sample_data_range]
            if self.sample_data_prefix is not None:
                for i, name in enumerate(sample_data_names):
                    if name.startswith(self.sample_data_prefix):
                        sample_data_names[i] = name[len(self.sample_data_prefix):]
        if self.wave_numbers_in_header:
            for i in spectral_data_range:
                match = re.match(self.wave_numbers_regexp, str(data['attributes'][i]))
                if match is None:
                    wave_numbers.append(i)
                else:
                    wave_numbers.append(float(match.group(1)))
        else:
            wave_numbers = [x for x in range(len(spectral_data_range))]

        # data
        result = []
        for row in data["data"]:
            sample_id = row[sample_id_index]
            amplitudes = [row[x] for x in spectral_data_range]
            sample_data = dict()
            if sample_data_range is not None:
                for i, r in enumerate(sample_data_range):
                    value = row[r]
                    if sample_data_types[i].upper() in ["NUMERIC", "REAL", "INTEGER"]:
                        value = float(value)
                    sample_data[sample_data_names[i]] = value
            result.append(Spectrum(sample_id, wave_numbers[:], amplitudes, sample_data))

        return result

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


class Writer(SpectrumWriter):
    """
    Writer that stores spectra in ARFF format (row-wise).
    """
    # Options
    sample_id = Option(help='The attribute name to use for the sample ID column', default='sample_id')
    sample_data = Option(help='The names of the sample data values to output', default=None, nargs='*')
    wave_numbers_format = Option(help='The format to use for the wave number attributes, the following placeholders are available: ' + "|".join(PLACEHOLDERS), default=PH_WAVE_NUMBER)
    sample_data_prefix = Option(help='The prefix to use for the sample data attributes', default='')

    def _write(self, spectra, spec_file, as_bytes):
        """
        Writes the spectra to the filehandle.

        :param spectra: the list of spectra
        :type spectra: list
        :param spec_file: the file handle to use
        :type spec_file: file
        :param as_bytes: whether to write as bytes or string
        :type as_bytes: bool
        """
        # ensure that all spectra have same number wave numbers
        if len(spectra) > 1:
            for i in range(1, len(spectra)):
                if len(spectra[0].waves) != len(spectra[1].waves):
                    raise Exception("Number of wave numbers differ (#%d vs #%d): %d != %d" % (0, i, len(spectra[0].waves), len(spectra[1].waves)))

        data = dict()
        data["relation"] = "wai.spectralio"
        data["description"] = ""

        # header
        data["attributes"] = list()
        data["attributes"].append((self.sample_id, 'STRING'))
        for i, w in enumerate(spectra[0].waves):
            col = self.wave_numbers_format
            col = col.replace(PH_INDEX, str(i))
            col = col.replace(PH_WAVE_NUMBER, locale.str(w))
            data["attributes"].append((col, 'NUMERIC'))
        if self.sample_data is not None:
            sample_data_types = dict()
            for sd in self.sample_data:
                col = self.sample_data_prefix + sd
                # determine type of sample data
                sample_data_types[sd] = "NUMERIC"
                for spectrum in spectra:
                    if sd in spectrum.sample_data:
                        if isinstance(spectrum.sample_data[sd], str):
                            sample_data_types[sd] = "STRING"
                            break
                data["attributes"].append((col, sample_data_types[sd]))

        # data
        data["data"] = list()
        for spectrum in spectra:
            row = [spectrum.id]
            for ampl in spectrum.amplitudes:
                row.append(locale.str(ampl))
            if self.sample_data is not None:
                for sd in self.sample_data:
                    if sd in spectrum.sample_data:
                        row.append(str(spectrum.sample_data[sd]))
                    else:
                        row.append(None)
            data["data"].append(row)

        arff.dump(data, spec_file)

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
