import datetime
from typing import Type, IO, List, Optional

from .api import SpectrumReader, SpectrumWriter, Spectrum
from .serialisation.serialisers import NullTerminatedStringSerialiser, IntSerialiser, FloatSerialiser

DATE_FORMAT_COMMENT = "%a %b %d %H:%M:%S %Y"
DATE_FORMAT_COMMENT_2 = "%a %b %d %H:%M:%S %Y (%Z)"
DATE_FORMAT_INTERNAL: str = "%Y-%m-%d %H:%M:%S"


class Reader(SpectrumReader):
    """
    Reads spectra in DPT format.
    """
    # Serialisers
    _string_serialiser: NullTerminatedStringSerialiser = NullTerminatedStringSerialiser("ascii")
    _short_serialiser: IntSerialiser = IntSerialiser(num_bytes=2, signed=False)
    _int_serialiser: IntSerialiser = IntSerialiser(signed=False)
    _float_serialiser: FloatSerialiser = FloatSerialiser(double_precision=False)

    def _read(self, spec_file: IO[bytes], filename: str) -> List[Spectrum]:
        data = spec_file.read()

        sp = Spectrum(self._string_serialiser.deserialise_from_bytes(data[30:]))

        num_blocks = self._short_serialiser.deserialise_from_bytes(data[294:])
        self.logger.info(f"# blocks: {num_blocks}")

        offset_comments = -1
        offset_data_desc = -1
        offset_data = -1
        offset_block = 304
        for i in range(num_blocks):
            block_type = self._short_serialiser.deserialise_from_bytes(data[offset_block:])

            if block_type == 0x001B:
                offset_comments = self._short_serialiser.deserialise_from_bytes(data[offset_block + 2:])
                self.logger.info(f"offset comments: {offset_comments}")
            elif block_type == 0x0003:
                offset_data = self._short_serialiser.deserialise_from_bytes(data[offset_block + 2:])
                self.logger.info(f"offset data: {offset_data}")
            elif block_type == 0x0002:
                offset_data_desc = self._short_serialiser.deserialise_from_bytes(data[offset_block + 2:])
                self.logger.info(f"offset data description: {offset_data_desc}")

            offset_block += 16

        if offset_comments == -1:
            raise RuntimeError("Failed to determine offset for comments!")
        if offset_data == -1:
            raise RuntimeError("Failed to determine offset for data!")
        if offset_data_desc == -1:
            raise RuntimeError("Failed to determine offset for data description!")

        # Comments
        comments = self._string_serialiser.deserialise_from_bytes(data[offset_comments:]).split("\r\n")
        self.logger.info(f"Comments:\n" + "\n".join(comments))
        section = ""
        for comment in comments:
            if not comment.startswith("\t"):
                section = comment
                continue

            comment = comment.strip()

            if " on " in comment:
                key = comment[:comment.index(" on ")].strip()
                sval = comment[comment.index(" on ") + 4:].strip()
                formatted = self._format_time(sval)
                if formatted is not None:
                    sp.sample_data[f"{section}{' - ' if section != '' else ''}{key}"] = formatted
            elif ":" in comment:
                key = comment[:comment.index(":")].strip()
                sval = comment[comment.index(":") + 1:].strip()
                sp.sample_data[f"{section}{' - ' if section != '' else ''}{key}"] = sval

        # Num points
        num_points = self._int_serialiser.deserialise_from_bytes(data[offset_data_desc + 4:])
        self.logger.info(f"# points: {num_points}")

        # Min/max wave number
        max_wave = self._float_serialiser.deserialise_from_bytes(data[offset_data_desc + 16:])
        min_wave = self._float_serialiser.deserialise_from_bytes(data[offset_data_desc + 20:])
        self.logger.info(f"Wave numbers: {min_wave } - {max_wave}")

        for i in range(num_points):
            ampl = self._float_serialiser.deserialise_from_bytes(data[offset_data + i * 4:])
            if ampl == float("NaN"):
                continue

            sp.waves.append(max_wave - (max_wave - min_wave) * i / num_points)
            sp.amplitudes.append(ampl)

            self.logger.info(f"{i}: {sp.waves[-1]}, {sp.amplitudes[-1]}")

        return [sp]

    @staticmethod
    def _format_time(time_string: str) -> Optional[str]:
        """
        Formats the given time string.

        :param time_string:     The string to format.
        :return:                The formatted string.
        """
        try:
            return datetime.datetime.strptime(time_string, DATE_FORMAT_COMMENT).strftime(DATE_FORMAT_INTERNAL)
        except ValueError:
            try:
                return datetime.datetime.strptime(time_string, DATE_FORMAT_COMMENT_2).strftime(DATE_FORMAT_INTERNAL)
            except ValueError:
                return None

    @classmethod
    def get_writer_class(cls) -> 'Type[SpectrumWriter]':
        raise NotImplementedError(Reader.get_writer_class.__qualname__)

    def binary_mode(self, filename: str) -> bool:
        return True


read = Reader.read
