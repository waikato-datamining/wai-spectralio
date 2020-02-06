import locale
import re
from typing import Dict, Optional, List, Tuple, Type

from .api import LoggingObject, SpectrumReader, SpectrumWriter, Spectrum
from .mixins import ProductCodeOptionsMixin, LocaleOptionsMixin
from .options import Option
from .util import with_locale

# The prefix string specifying a comment
COMMENT: str = "##"


class ParsedFile(LoggingObject):
    """
    Class for parsing an ASC file.
    """
    def __init__(self):
        self._ht: Dict[str, str] = {}
        self._dp: List[Tuple[float, float]] = []
        self._last_error: str = ""

    @property
    def last_error(self) -> str:
        return self._last_error

    @property
    def type(self) -> str:
        return self._ht["Product Name"]

    @property
    def id(self) -> str:
        return self._ht["Sample ID"]

    @property
    def num_datapoints(self) -> Optional[int]:
        try:
            return int(self._ht["Nr of data points"])
        except ValueError:
            return None

    def get_wavenumber_list(self) -> List[float]:
        """
        Returns the wave number list.

        :return:    The list.
        """
        return list(db[0] for db in self._dp)

    def get_properties(self) -> Dict[str, str]:
        """
        Get dictionary property data.

        :return:    The dictionary.
        """
        return self._ht

    def get_NIR_list(self) -> List[float]:
        """
        Returns the NIR list.

        :return:    The list.
        """
        return list(db[1] for db in self._dp)

    def parse_with_locale(self, string: str, locale: Optional[str] = None) -> bool:
        """
        Parses the given string in the given locale.

        :param string:      The string to parse.
        :param locale:      The locale to parse in.
        :return:            True if successfully parsed.
        """
        parse = with_locale(locale)(self.parse) if locale is not None else self.parse
        return parse(string)

    def parse(self, string: str) -> bool:
        """
        Parses the given string.

        :param string:      The string to parse.
        :return:            True if successfully parsed.
        """
        lines = string.split("\n")
        processing_header: bool = True
        for line in lines:
            if line.startswith(COMMENT):
                if processing_header:
                    line = line[2:].strip()
                    vals: List[str] = line.split("=")
                    if len(vals) != 2:
                        continue
                    self._ht[vals[0].strip()] = vals[1].strip()
                else:
                    self._last_error = "Found Header Line inside Data"
                    return False
            else:
                processing_header = False
                vals: List[str] = re.split(r"\s", line.strip())
                if len(vals) != 2:
                    self._last_error = f"Data line corrupt:{line} split into:{len(vals)}"
                    for val in vals:
                        self._last_error += f"({val})"
                    return False
                try:
                    self._dp.append((locale.atof(vals[0]), locale.atof(vals[1])))
                except Exception as e:
                    self._last_error = f"Data line corrupt: {line}"
                    self.logger.exception(self._last_error, exc_info=e)
                    return False
        return True


class Reader(LocaleOptionsMixin, SpectrumReader):
    """
    Reads spectra in BLGG ASC format.
    """
    def _fix_key(self, key: str) -> str:
        """
        Turns the key into a proper SampleData constant.

        :param key: The key to transform if necessary.
        :return:    The fixed key.
        """
        if key in {"SampleType", "Product Name"}:
            return "Sample Type"

        return key

    def _read(self, spec_file, filename):
        pf = ParsedFile()
        pf.parse_with_locale(spec_file.read(), self.locale)

        # NIR list
        nir = pf.get_NIR_list()
        if len(nir) == 0:
            raise RuntimeError("No spectral data loaded from file.")
        if pf.num_datapoints != len(nir):
            raise RuntimeError(f"Mismatched wavenumber length. Expected {pf.num_datapoints}, read {len(nir)}")

        # Wavenumbers
        waves = pf.get_wavenumber_list()

        sd = {self._fix_key(key): value for key, value in pf.get_properties().items()}

        return [Spectrum(pf.id, waves, nir, sd)]

    def binary_mode(self, filename: str) -> bool:
        return False

    @classmethod
    def get_writer_class(cls) -> 'Type[Writer]':
        return Writer


class Writer(ProductCodeOptionsMixin, LocaleOptionsMixin, SpectrumWriter):
    """
    Writer that stores spectrums in the BLGG ASC format.
    """
    # Options
    instrument_name = Option(help="Instrument Name to be used in ASC header", default="<not implemented>")
    accessory_name = Option(help="Accessory Name to be used in ASC header", default="ABB-BOMEM MB160D")
    data_points = Option(help="number of data points. -1 means use as many as in spectrum", type=int, default=-1)
    first_x_point = Option(help="first wavenumber", type=float, default=3749.3428948242)
    last_x_point = Option(help="last wavenumber", type=float, default=9998.2477195313)
    descending = Option(help="if set to true, the spectrum is output in descending x-axis order", action="store_true")

    def gen_product_code(self, data: Spectrum) -> str:
        """
        Generates the product code for the spectrum.

        :param data:    The spectrum.
        :return:        The product code.
        """
        product_code = self.product_code
        if self.product_code_from_field:
            if data.sample_data is None:
                return "<Report Not Available"

            if product_code not in data.sample_data:
                return f"<Field '{product_code}' Not Available in Report"

            product_code = data.sample_data[product_code]

        return product_code

    def gen_sample_id(self, data: Spectrum) -> str:
        """
        Generates the sample ID for the spectrum.

        :param data:    The spectrum.
        :return:        The sample ID.
        """
        return data.id.replace("'", "")

    def gen_num_datapoints(self, data: Spectrum) -> int:
        """
        Generate the number of data-points from the spectrum.

        :param data:    The spectrum.
        :return:        The number of data-points.
        """
        points = self.data_points

        if points == -1:
            return len(data)

        if len(data) != points:
            message = f"Spectrum does not have the expected number of points: {len(data)} != {points}"
            self.logger.critical(message)
            raise RuntimeError(message)

        return points

    def get_sorted_datapoints(self, data: Spectrum) -> List[Tuple[float, float]]:
        """
        Gets the data-points from the spectrum, sorted by wavenumber.

        :param data:    The spectrum.
        :return:        The data-points.
        """
        # Get the unsorted data-points
        datapoints = [(wave, ampl) for wave, ampl in zip(data.waves, data.amplitudes)]

        # Sort them
        datapoints.sort(key=lambda pair: pair[0], reverse=self.descending)

        return datapoints

    def gen_ASC_string(self, data: Spectrum) -> str:
        """
        Generate the ASC String to output.

        :param data:    The data to write.
        :return:        ASC file as a string.
        """
        ret = (f"{COMMENT} Instrument Name = {self.instrument_name}\n"
               f"{COMMENT} Accessory Name = {self.accessory_name}\n"
               f"{COMMENT} Product Name = {self.gen_product_code(data)}\n"
               f"{COMMENT} Sample ID = {self.gen_sample_id(data)}\n")

        points = self.gen_num_datapoints(data)

        ret += (f"{COMMENT} Nr of data points = {points}\n"
                f"{COMMENT} First X Point = {self.first_x_point}\n"
                f"{COMMENT} Last X Point = {self.last_x_point}\n"
                f"{COMMENT} Wave number - Absorbance value\n")

        nf = with_locale(self.locale)(locale.str)

        vsp = self.get_sorted_datapoints(data)

        currwn = self.first_x_point
        diff = (self.last_x_point - currwn) / (points - 1)
        for point in vsp:
            ret += f"{nf(currwn)} {nf(point[1])}\n"
            currwn += diff

        return ret

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
        if len(spectra) != 1:
            raise ValueError("Writer can only write exactly 1 spectrum at a time!")

        spec_file.write(self.gen_ASC_string(spectra[0]))

    def binary_mode(self, filename: str) -> bool:
        return False

    @classmethod
    def get_reader_class(cls) -> Type[Reader]:
        return Reader


read = Reader.read


write = Writer.write
