from wai.spectralio.api import Spectrum, SpectrumReader, SpectrumWriter
from javaproperties import Properties, dumps, loads
import gzip


SEPARATOR = "---"
""" the separator between multiple spectra in file. """

COMMENT = "# "
""" the string for prefixing the meta-data with. """

HEADER = "waveno,amplitude"
""" the column header. """

DATATYPE_SUFFIX = "\tDataType"
""" the suffix for the data type in the properties. """

FIELD_SAMPLE_ID = "Sample ID"
""" the name of the field storing the sample ID. """


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

        # split meta data and spectral data
        comments = True
        meta = []
        data = []
        for i in range(len(lines)):
            if comments and lines[i].startswith(COMMENT):
                meta.append(lines[i])
            elif lines[i].startswith(HEADER):
                comments = False
                continue
            elif not comments:
                data.append(lines[i])

        # meta data
        for i in range(len(meta)):
            meta[i] = meta[i][2:]
        props = loads("".join(meta))
        id = "noid"
        if FIELD_SAMPLE_ID in props:
            id = str(props[FIELD_SAMPLE_ID])
        metadata = {}
        for k in props:
            if k.endswith(DATATYPE_SUFFIX):
                continue
            v = props[k]
            t = "U"
            if k + DATATYPE_SUFFIX in props:
                t = props[k + DATATYPE_SUFFIX]
            if t == "N":
                metadata[k] = float(v)
            elif t == "B":
                metadata[k] = bool(v)
            else:
                metadata[k] = str(v)

        # spectral data
        waves = []
        ampls = []
        for line in data:
            if "," in line:
                (wave, ampl) = line.split(",")
                waves.append(float(wave))
                ampls.append(float(ampl))

        return Spectrum(id, waves, ampls, metadata)

    def _read(self, specfile):
        """
        Reads the spectra from the file handle.

        :param specfile: the file handle to read from
        :type specfile: file
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

    def read(self, fname):
        """
        Reads the spectra from the specified file.

        :param fname: the file to read
        :type fname: str
        :return: the list of spectra
        :rtype: list
        """

        if fname.endswith(".gz"):
            with gzip.open(fname, "rb") as specfile:
                return self._read(specfile)
        else:
            with open(fname, "r") as specfile:
                return self._read(specfile)


class Writer(SpectrumWriter):
    """
    Writer for ADAMS spectra.
    """

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

        first = True
        for spectrum in spectra:
            if not first:
                specfile.write(SEPARATOR + "\n")

            # prefix meta-data with '# '
            props = Properties()
            for k in spectrum.metadata():
                v = spectrum.metadata()[k]
                props[k] = str(v)
                if isinstance(v, int) or isinstance(v, float):
                    props[k + DATATYPE_SUFFIX] = "N"
                elif isinstance(v, bool):
                    props[k + DATATYPE_SUFFIX] = "B"
                elif isinstance(v, str):
                    props[k + DATATYPE_SUFFIX] = "S"
                else:
                    props[k + DATATYPE_SUFFIX] = "U"
            metastr = dumps(props)
            lines = metastr.split("\n")
            for i in range(len(lines)):
                lines[i] = COMMENT + lines[i]

            # meta-data
            for line in lines:
                if as_bytes:
                    specfile.write((line + "\n").encode())
                else:
                    specfile.write(line + "\n")

            # header
            if as_bytes:
                specfile.write((HEADER + "\n").encode())
            else:
                specfile.write(HEADER + "\n")

            # spectral data
            for i in range(len(spectrum)):
                if as_bytes:
                    specfile.write(("%s,%s\n" % (spectrum.waves()[i], spectrum.amplitudes()[i])).encode())
                else:
                    specfile.write("%s,%s\n" % (spectrum.waves()[i], spectrum.amplitudes()[i]))

            first = False

    def write(self, spectra, fname):
        """
        Writes the spectra to the specified file.

        :param spectra: the list of spectra
        :type spectra: list
        :param fname: the file to write to
        :type fname: str
        """

        if fname.endswith(".gz"):
            with gzip.open(fname, "wb") as specfile:
                self._write(spectra, specfile, True)
        else:
            with open(fname, "w") as specfile:
                self._write(spectra, specfile, False)
