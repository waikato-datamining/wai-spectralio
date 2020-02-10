from typing import Type, IO, List, Any, Dict, Optional

from .api import SpectrumReader, SpectrumWriter, Spectrum
from .options import Option
from .serialisation.serialisers import IntSerialiser, FloatSerialiser

PREFIX_TRACE: str = "Trace."
BLOCKS_OFFSET: int = 0x24


class Reader(SpectrumReader):
    """
    Reads spectra in OPUS format.
    """
    # Options
    sample_id = Option(help="ID|Field1|Field2|Field3|[prefix]", default="SNM")
    start = Option(help="spectrum number to start loading from", type=int, default=1)
    max = Option(help="maximum spectra to load", type=int, default=-1)
    add_trace_to_report = Option(
        help=f"if enabled the trace of identified blocks etc gets added to the report, using prefix {PREFIX_TRACE}.",
        action="store_true"
    )

    # Class serialisers
    _int_serialiser = IntSerialiser(signed=False)
    _double_serialiser = FloatSerialiser()
    _float_serialiser = FloatSerialiser(double_precision=False)

    def __init__(self, options=None):
        super().__init__(options)

        self._trace: Dict[str, Any] = {}

    def _read(self, spec_file: IO[bytes], filename: str) -> List[Spectrum]:
        try:
            return self._read_unhandled(spec_file, filename)
        except Exception:
            self.logger.exception(f"Failed to read '{filename}'!")
            return []

    def _read_unhandled(self, spec_file: IO[bytes], filename: str) -> List[Spectrum]:
        """
        Reads the spectra from the file handle. Doesn't handle exceptions.

        :param spec_file:   The file handle to read from.
        :param filename:    The file being read.
        :return:            A list of spectra in the file.
        """
        self._trace = {}

        buf: bytes = spec_file.read()

        data_start: int = self._get_AB_data_offset(buf)
        self.logger.info(f"data_start={data_start}")

        nir: List[float] = self._get_NIR_list(buf)
        wn: List[float] = self._get_wave_numbers(buf)

        num_p: int = self._get_AB_count(buf)
        self.logger.info(f"points={num_p}")

        id_: str = self._get_value_for(self.sample_id, buf)

        if id_ is None:
            self.logger.info(f"{self.sample_id}=null")
            id_ = "ERR"
        else:
            self.logger.info(f"{self.sample_id}='{id_}'")

        meta = self._get_metadata(buf)

        sp = Spectrum(id_, wn, nir, meta)

        for key, val in self._trace.items():
            self.logger.info(f"{key}={val}")

            if self.add_trace_to_report:
                sp.sample_data[PREFIX_TRACE + key] = val

        return [sp]

    def _get_metadata(self, buf: bytes) -> Dict[str, Any]:
        """
        Returns the meta-data from the buffer.

        :param buf:     The buffer to read from.
        :return:        The metadata.
        """
        result = {}

        offset: int = self._get_text_block_offset(buf)

        length: int = self._get_text_block_size(buf) * 4

        buf = buf[offset:offset + length]

        s: str = buf.decode()

        if '{' not in s or '}' not in s:
            return result

        s = s[s.index('{') + 1: s.index('}')]

        parts = self._split(s)

        for part in parts:
            pair: List[str] = part.split('=')

            if len(pair) == 2:
                if pair[1].startswith("'") and pair[1].endswith("'"):
                    result[pair[0]] = pair[1][1:-1]
                else:
                    try:
                        result[pair[0]] = float(pair[1])
                    except:
                        pass

        return result

    @staticmethod
    def _split(s: str) -> List[str]:
        """
        Attempts to split a string, using the specified delimiter character.
        A delimiter gets ignored if inside double quotes.

        :param s:       The string to split.
        :return:        The parts (single list element if no range)
        """
        result = []

        current = ""
        escaped = False
        for i in range(len(s)):
            c = s[i]

            if c == "'":
                escaped = not escaped
                current += c
            elif c == ',':
                if escaped:
                    current += c
                else:
                    result.append(current.strip())
                    current = ""
            else:
                current += c

        # Add last string
        if len(current) > 0:
            result.append(current.strip())

        return result

    def _get_value_for(self, key: str, buf: bytes) -> Optional[str]:
        """
        Get value for key, from Text Block. Or null if not found.

        :param key:     The key to look up.
        :param buf:     Bytes.
        :return:        The value.
        """
        offset: int = self._get_text_block_offset(buf)
        length: int = self._get_text_block_size(buf) * 4

        for i in range(offset, offset + length):
            if self._find(f"{key}='", buf, i):
                result: str = ""
                pos: int = i + len(key) + 2
                while buf[pos] != 0x27:
                    result += buf[pos:pos + 1].decode()
                    pos += 1
                    if pos == len(buf) - 1:
                        return None
                return result
        return None

    def _get_text_block_offset(self, buf: bytes) -> int:
        """
        Get position of Text Data.

        :param buf:     Bytes.
        :return:        The text data pos.
        """
        result: int = -1
        offset: int = self._get_text_offset(buf)
        if offset != -1:
            result = self._get_int(buf, offset + 4)
        self._trace["getTextBlockOffset"] = result
        return result

    def _get_text_block_size(self, buf: bytes) -> int:
        """
        Size of Text Block (in 4-byte words).

        :param buf:     Bytes of bruker file image.
        :return:        The text block size (in 4-byte words).
        """
        result: int = -1
        offset: int = self._get_text_offset(buf)
        if offset != -1:
            result = self._get_int(buf, offset)
        self._trace["getTextBlockSize"] = result
        return result

    def _get_text_offset(self, buf: bytes) -> int:
        """
        Find position of Text Block offset.

        :param buf:     Bytes.
        :return:        Text Block offset.
        """
        result: int = self._get_block_offset(buf, b'\xFF\xFF\x68\x40')
        self._trace["getTextOffset"] = result
        return result

    @staticmethod
    def _find(find: str, buf: bytes, start: int) -> bool:
        """
        Find a given string in byte array, from a starting pos.

        :param find:    The string to find.
        :param buf:     The bytes.
        :param start:   The starting offset.
        :return:        Found?
        """
        if start + len(find) > len(buf):
            return False

        b_find: bytes = find.encode()

        return buf[start:start + len(b_find)] == b_find

    def _get_wave_numbers(self, buf: bytes) -> List[float]:
        """
        Gets the wave numbers from the file.

        :param buf:     File bytes.
        :return:        Wave numbers.
        """
        offset: int = self._get_AB_data_offset(buf)
        if offset == -1:
            self.logger.critical("Failed to determine ABDataOffset!")
            return []

        offset_first: int = self._get_block_offset_reverse(buf, offset, b'\x46\x58\x56\x00')
        if offset_first == -1:
            self.logger.critical("Failed to determine offset for first data point (FXV)!")
            return []

        offset_last: int = self._get_block_offset_reverse(buf, offset, b'\x4C\x58\x56\x00')
        if offset_last == -1:
            self.logger.critical("Failed to determine offset for last data point (LXV)!")
            return []

        offset_num: int = self._get_block_offset_reverse(buf, offset, b'\x4E\x50\x54\x00')
        if offset_num == -1:
            self.logger.critical("Failed to determine offset for number of data points (NPT)!")
            return []

        new_count: int = self._get_int(buf, offset_num + 8)
        fd = self._double_serialiser
        first_x: float = fd.deserialise_from_bytes(buf[offset_first + 8: offset_first + 16])
        last_x: float = fd.deserialise_from_bytes(buf[offset_last + 8: offset_last + 16])
        diff: float = (last_x - first_x) / (new_count - 1)

        return [first_x + i * diff for i in range(new_count)]

    def _get_AB_count(self, buf: bytes) -> int:
        """
        Get number of spectral values.

        :param buf:     Bytes.
        :return:        Number of spectral values.
        """
        result: int = -1
        offset: int = self._get_AB_data_offset(buf)
        offset_num: int = -1
        if offset != -1:
            offset_num = self._get_block_offset_reverse(buf, offset, b'\x4E\x50\x54\x00')
        if offset_num != -1:
            result = self._get_int(buf, offset_num + 8)
        self._trace["getABCount"] = result
        return result

    def _get_block_offset_reverse(self, buf: bytes, start: int, match: bytes):
        """
        Starting from start, find sequence of bytes.
        Return position of sequence, or -1 if not found.

        :param buf:     Bytes.
        :param start:   Start position.
        :param match:   Bytes to match.
        :return:        Position of sequence, or -1 if not found.
        """
        # Match bytes must be length-4 sequence
        if len(match) != 4:
            raise ValueError(f"Match bytes must be length-4")

        result: int = start
        found: bool = False
        while not found:
            if result <= 4:
                result = -1
                break

            found = (match == buf[result:result + len(match)])

            if not found:
                result -= 1

        self._trace[f"getBlockOffsetReverse:{match.hex()}"] = result

        return result

    def _get_NIR_list(self, buf: bytes) -> List[float]:
        """
        Get list of NIR data from bytes of bruker file image.

        :param buf: Bytes.
        :return:    NIR data list.
        """
        ndp: int = self._get_AB_count(buf)

        if ndp == -1:
            self.logger.critical("Failed to determine number of data-points!")
            return []

        ret = []

        datastart: int = self._get_AB_data_offset(buf)

        if datastart == -1:
            return []

        try:
            for count in range(ndp):
                ret.append(self._get_float(buf, datastart + count * 4))
        except Exception:
            return []

        return ret

    def _get_AB_data_offset(self, buf: bytes) -> int:
        """
        Get position of NIR data.

        :param buf:     Bytes of file image.
        :return:        NIR data pos.
        """
        result: int = -1
        offset: int = self._get_AB_offset(buf)
        if offset != -1:
            result = self._get_int(buf, offset + 4)
        self._trace["getABDataOffset"] = result
        return result

    @classmethod
    def _get_int(cls, buf: bytes, offset: int) -> int:
        """
        Get int from 4bytes, LSByte first.

        :param buf:     Bytes.
        :param offset:  Grab from.
        :return:        Integer.
        """
        return cls._int_serialiser.deserialise_from_bytes(buf[offset:offset + 4])

    @classmethod
    def _get_float(cls, buf: bytes, offset: int) -> float:
        """
        Get float.

        :param buf:     Bytes.
        :param offset:  Grab from.
        :return:        Float.
        """
        return cls._float_serialiser.deserialise_from_bytes(buf[offset:offset + 4])

    def _get_AB_offset(self, buf: bytes) -> int:
        """
        Find position of AB Block offset.

        :param buf:     Bytes.
        :return:        AB block offset.
        """
        result: int = self._get_block_offset(buf, b'\x0F\x10\x00\xFF')
        self._trace["getABOffset"] = result
        return result

    def _get_block_offset(self, buf: bytes, match: bytes) -> int:
        """
        Starting from blocks_offset, find sequence of bytes
        Return position of sequence, or -1 if not found.

        :param buf:     The bytes to search.
        :param match:   The bytes to search for.
        :return:        Position of sequence, or -1 if not found.
        """
        # Match bytes must be length-4 sequence
        if len(match) != 4:
            raise ValueError(f"Match bytes must be length-4")

        result: int = -1
        offset: int = BLOCKS_OFFSET
        found: bool = False
        while not found:
            if offset >= len(buf) - 1:
                break

            found = all(m == b or m == 0xFF
                        for m, b in zip(match, buf[offset:offset+len(match)]))

            if found:
                break

            offset += 12

        if found:
            result = offset + 4

        self._trace[f"getBlockOffset:{match.hex()}"] = result

        return result

    @classmethod
    def get_writer_class(cls) -> 'Type[SpectrumWriter]':
        raise NotImplementedError(Reader.get_writer_class.__qualname__)

    def binary_mode(self, filename: str) -> bool:
        return True


read = Reader.read
