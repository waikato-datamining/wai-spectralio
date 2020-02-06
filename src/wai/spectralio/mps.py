from typing import Type, IO, List
import datetime

from .api import SpectrumReader, SpectrumWriter, Spectrum

SEPARATOR: str = ": "
KEY_SAMPLE_IDENT: str = "SampleIdent"
KEY_TIME_MEASURED: str = "TimeMeasured"
KEY_ZERO_FIT: str = "ZeroFit"
KEY_GAIN_FIT: str = "GainFit"
DATE_FORMAT_TIME_MEASURED: str = "%d-%b-%Y %H:%M:%S"
DATE_FORMAT_INTERNAL: str = "%Y-%m-%d %H:%M:%S"


class Reader(SpectrumReader):
    """
    Reads spectra in DPT format.
    """
    def _read(self, spec_file: IO[str], filename: str) -> List[Spectrum]:
        sp = Spectrum()

        index = 0
        zero_fit = 0.0
        gain_fit = 0.0
        for line in spec_file:
            # Skip empty lines
            if line.strip() == "":
                continue

            if SEPARATOR in line:
                parts = line.split(SEPARATOR)

                for i in range(len(parts)):
                    parts[i] = parts[i].strip()

                if len(parts) != 2:
                    continue

                if parts[0].startswith(KEY_SAMPLE_IDENT):
                    sp.id = parts[1]
                elif parts[0].startswith(KEY_TIME_MEASURED):
                    try:
                        formatted_time = self._format_time(parts[1])
                    except ValueError:
                        self.logger.warning(f"Cannot parse date: {parts[1]}")
                        formatted_time = parts[1]

                    sp.sample_data["Insert Timestamp"] = formatted_time
                    sp.sample_data[parts[0]] = formatted_time
                else:
                    try:
                        float_value = float(parts[1])
                    except ValueError:
                        sp.sample_data[parts[0]] = parts[1]
                    else:
                        sp.sample_data[parts[0]] = float_value

                        if parts[0].startswith(KEY_ZERO_FIT):
                            zero_fit = float_value
                        elif parts[0].startswith(KEY_GAIN_FIT):
                            gain_fit = float_value

            # SEPARATOR not in line
            else:
                sp.waves.append(zero_fit + index * gain_fit)
                sp.amplitudes.append(float(line))
                index += 1

        return [sp]

    @staticmethod
    def _format_time(time_string: str) -> str:
        """
        Formats the given time string.

        :param time_string:     The string to format.
        :return:                The formatted string.
        """
        return datetime.datetime.strptime(time_string, DATE_FORMAT_TIME_MEASURED).strftime(DATE_FORMAT_INTERNAL)

    @classmethod
    def get_writer_class(cls) -> 'Type[SpectrumWriter]':
        raise NotImplementedError(Reader.get_writer_class.__qualname__)

    def binary_mode(self, filename: str) -> bool:
        return False


read = Reader.read
