from .api import Spectrum, SpectrumReader, SpectrumWriter
from .sampleidextraction import SampleIDExtraction


class Reader(SampleIDExtraction, SpectrumReader):
    """
    Reader for ADAMS spectra.
    """
    def _define_options(self):
        """
        Configures the options parser.

        :return: the option parser
        :rtype: argparse.ArgumentParser
        """

        result = super()._define_options()
        result.add_argument('--separator', help='the separator to use for identifying X and Y columns', default=';')

        return result

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
        sample_id = self.extract(fname)
        waves = []
        ampls = []
        for line in specfile.readlines():
            line = line.strip()
            if len(line) == 0:
                continue

            parts = line.split(self._options_parsed.separator)

            waves.append(float(parts[0]))
            ampls.append(float(parts[1]))

        return [Spectrum(sample_id, waves, ampls, {})]

    def binary_mode(self, filename: str) -> bool:
        return False


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

        result = super()._define_options()
        result.add_argument('--separator', help='the separator to use for identifying X and Y columns', default=';')

        return result

    def _write(self, spectra, specfile, as_bytes):
        """
        Writes the spectra to the filehandle.

        :param spectra: the list of spectra
        :type spectra: list
        :param specfile: the file handle to use
        :type specfile: file
        """
        if len(spectra) != 1:
            raise ValueError("Can only write a single spectrum")

        spectrum = spectra[0]

        for wave, ampl in reversed(list(zip(spectrum.waves, spectrum.amplitudes))):
            specfile.write(f"{wave}{self._options_parsed.separator}{ampl}\n")

    def binary_mode(self, filename: str) -> bool:
        return False


read = Reader.read


write = Writer.write
