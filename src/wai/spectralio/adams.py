from typing import Type

from javaproperties import Properties, dumps, loads

from .api import Spectrum, SpectrumReader, SpectrumWriter
from .options import Option

SEPARATOR = "---"
""" the separator between multiple spectra in file. """

COMMENT = "# "
""" the string for prefixing the sample data with. """

HEADER = "waveno,amplitude"
""" the column header. """

DATATYPE_SUFFIX = "\tDataType"
""" the suffix for the data type in the properties. """

FIELD_SAMPLE_ID = "Sample ID"
""" the name of the field storing the sample ID. """

FIELD_INSTRUMENT = "Instrument"
""" the name of the field storing the instrument name. """

FIELD_FORMAT = "Format"
""" the name of the field storing the format. """


class Reader(SpectrumReader):
    """
    Reader for ADAMS spectra.
    """

    def _read_single(self, lines):
        """
        Reads the spectra from the lines.

        :param lines: the list of strings to parse
        :type lines: list
        :return: the list of spectra
        :rtype: list
        """

        # split sample data and spectral data
        comments = True
        sample = []
        data = []
        for i in range(len(lines)):
            if comments and lines[i].startswith(COMMENT):
                sample.append(lines[i])
            elif lines[i].startswith(HEADER):
                comments = False
                continue
            elif not comments:
                data.append(lines[i])

        # sample data
        for i in range(len(sample)):
            sample[i] = sample[i][2:]
        props = loads("".join(sample))
        id = "noid"
        if FIELD_SAMPLE_ID in props:
            id = str(props[FIELD_SAMPLE_ID])
        sampledata = {}
        for k in props:
            if k.endswith(DATATYPE_SUFFIX):
                continue
            v = props[k]
            t = "U"
            if k + DATATYPE_SUFFIX in props:
                t = props[k + DATATYPE_SUFFIX]
            if t == "N":
                sampledata[k] = float(v)
            elif t == "B":
                sampledata[k] = bool(v)
            else:
                sampledata[k] = str(v)
        if FIELD_INSTRUMENT not in sampledata:
            sampledata[FIELD_INSTRUMENT] = self.instrument
        if not self.keep_format:
            sampledata[FIELD_FORMAT] = self.format

        # spectral data
        waves = []
        ampls = []
        for line in data:
            if "," in line:
                (wave, ampl) = line.split(",")
                waves.append(float(wave))
                ampls.append(float(ampl))

        return Spectrum(id, waves, ampls, sampledata)

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

        result = []
        lines = spec_file.readlines()
        subset = []
        for i in range(len(lines)):
            if lines[i] == SEPARATOR:
                if len(subset) > 0:
                    result.append(self._read_single(subset))
                subset = []
                continue
            if isinstance(lines[i], bytes):
                lines[i] = lines[i].decode("UTF-8")
            subset.append(lines[i])

        if len(subset) > 0:
            result.append(self._read_single(subset))

        return result

    def binary_mode(self, filename: str) -> bool:
        return filename.endswith(".gz")

    @classmethod
    def get_writer_class(cls) -> 'Type[Writer]':
        return Writer


class Writer(SpectrumWriter):
    """
    Writer for ADAMS spectra.
    """
    # Options
    output_sampledata = Option(action='store_true', help='whether to output the sample data as well')

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
        # Create a writing function which handles the as_bytes argument
        if as_bytes:
            def write(string: str):
                spec_file.write(string.encode())
        else:
            write = spec_file.write

        first = True
        for spectrum in spectra:
            if not first:
                write(SEPARATOR + "\n")

            if self._options_parsed.output_sampledata:
                # prefix sample data with '# '
                props = Properties()
                for k in spectrum.sample_data:
                    v = spectrum.sample_data[k]
                    props[k] = str(v)
                    if isinstance(v, int) or isinstance(v, float):
                        props[k + DATATYPE_SUFFIX] = "N"
                    elif isinstance(v, bool):
                        props[k + DATATYPE_SUFFIX] = "B"
                    elif isinstance(v, str):
                        props[k + DATATYPE_SUFFIX] = "S"
                    else:
                        props[k + DATATYPE_SUFFIX] = "U"
                samplestr = dumps(props)
                lines = samplestr.split("\n")
                for i in range(len(lines)):
                    lines[i] = COMMENT + lines[i]

                # sample data
                for line in lines:
                    write(line + "\n")

            # header
            write(HEADER + "\n")

            # spectral data
            for i in range(len(spectrum)):
                write("%s,%s\n" % (spectrum.waves[i], spectrum.amplitudes[i]))

            first = False

    def binary_mode(self, filename: str) -> bool:
        return filename.endswith(".gz")

    @classmethod
    def get_reader_class(cls) -> Type[Reader]:
        return Reader


read = Reader.read

write = Writer.write
