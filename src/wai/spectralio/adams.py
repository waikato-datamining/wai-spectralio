from wai.spectralio.api import Spectrum, SpectrumReader, SpectrumWriter
from javaproperties import Properties, dumps, loads


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
            sampledata[FIELD_INSTRUMENT] = self._options_parsed.instrument
        if not self._options_parsed.keep_format:
            sampledata[FIELD_FORMAT] = self._options_parsed.format

        # spectral data
        waves = []
        ampls = []
        for line in data:
            if "," in line:
                (wave, ampl) = line.split(",")
                waves.append(float(wave))
                ampls.append(float(ampl))

        return Spectrum(id, waves, ampls, sampledata)

    def _read(self, specfile, fname):
        """
        Reads the spectra from the file handle.

        :param specfile: the file handle to read from
        :type specfile: file
        :param fname: the file being read
        :type fname: str
        :return: the list of spectra
        :rtype: list
        """

        result = []
        lines = specfile.readlines()
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


class Writer(SpectrumWriter):
    """
    Writer for ADAMS spectra.
    """

    def _define_options(self):
        """
        Configures the options parser.

        :return: the option parser
        :rtype: argparse.ArgumentParser
        """

        result = super(Writer, self)._define_options()
        result.add_argument('--output_sampledata', action='store_true', help='whether to output the sample data as well')

        return result

    def _write(self, spectra, specfile, as_bytes):
        """
        Writes the spectra to the filehandle.

        :param spectra: the list of spectra
        :type spectra: list
        :param specfile: the file handle to use
        :type specfile: file
        :param as_bytes: whether to write as bytes or string
        :type as_bytes: bool
        """
        # Create a writing function which handles the as_bytes argument
        if as_bytes:
            def write(string: str):
                specfile.write(string.encode())
        else:
            write = specfile.write

        first = True
        for spectrum in spectra:
            if not first:
                write(SEPARATOR + "\n")

            if self._options_parsed.output_sampledata:
                # prefix sample data with '# '
                props = Properties()
                for k in spectrum.sampledata:
                    v = spectrum.sampledata[k]
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


read = Reader.read

write = Writer.write
