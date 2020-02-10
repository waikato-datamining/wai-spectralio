from typing import Type, IO, List

from .api import SpectrumReader, SpectrumWriter, Spectrum
from .options import Option
from .opus_ext_utils import *
from .opus_ext_utils.constants import *

FIELD_OPUS_FIRST_X = "Opus.FirstX"
FIELD_OPUS_LAST_X = "Opus.LastX"
FIELD_OPUS_NUM_POINTS = "Opus.NumPoints"
FIELD_OPUS_DIFF = "Opus.Diff"
FIELD_OPUS_SCALE = "Opus.Scale"
FIELD_OPUS_BLOCK_TYPE_DPF = "Opus.BlockType.DPF"
FIELD_OPUS_BLOCK_TYPE_HEX = "Opus.BlockType.Hex"
FIELD_OPUS_LOG = "Opus.Log"
PREFIX_OPUS = "Opus."


class Reader(SpectrumReader):
    """
    Reads spectra in OPUS format.
    """
    # Options
    spectrum_block_type: str = Option(
        help=f"the block type of the spectrum to extract, in hex notation; "
             f"e.g.: {to_hex_string(BLOCK_TYPE_MAIN_MASK)}; "
             f"the following report field contains this hex code: {FIELD_OPUS_BLOCK_TYPE_HEX}",
        default=to_hex_string(BLOCK_TYPE_MAIN_MASK)
    )
    operation: str = Option(
        help="the command-line operation to get the sample ID from, e.g., 'MeasureSample'",
        default=OPERATION_MEASURE_SAMPLE
    )
    key: str = Option(
        help="the command-line key to get the sample ID from, e.g, 'NAM'",
        default=KEY_SAMPLE_ID_2
    )
    all_spectra: bool = Option(
        help="if enabled, all spectra stored in the file are loaded",
        action="store_true"
    )
    add_command_lines: bool = Option(
        help="if enabled, the other command-lines extracted from the file gets added to the report",
        action="store_true"
    )
    add_log: bool = Option(
        help="if enabled, the entire log extracted from the file gets added to the report",
        action="store_true"
    )

    def _read(self, spec_file: IO[bytes], filename: str) -> List[Spectrum]:
        buffer = spec_file.read()

        definitions = self.read_definitions(buffer)
        for i, definition in enumerate(definitions):
            self.logger.info(f"Definition #{i}: {definition}")

        blocks = self.read_blocks(buffer, definitions)
        for i, block in enumerate(blocks):
            self.logger.info(f"Block #{i}: {block}")

        return self.find_spectra(blocks)

    @staticmethod
    def read_definitions(buffer: bytes) -> List[BlockDefinition]:
        """
        Parses the opus header and returns the blocks definitions.

        :param buffer:  The file contents.
        :return:        A list of block definitions.
        """
        result = []

        i = BLOCK_OFFSET
        while i < HEADER_LENGTH:
            type_ = get_int(buffer, i)
            length = get_int(buffer, i + 4)
            offset = get_int(buffer, i + 8)
            if length == 0:
                break

            definition = BlockDefinition()
            definition.type = type_
            definition.length_blocks = length
            definition.length_bytes = length * 4
            definition.offset = offset
            result.append(definition)

            i += BLOCK_DEFINITION_LENGTH

        return result

    @staticmethod
    def read_blocks(buffer: bytes, definitions: List[BlockDefinition]) -> List[Block]:
        """
        Creates blocks from the definitions.

        :param buffer:          The file contents.
        :param definitions:     The definitions to use.
        :return:                The blocks.
        """
        result = []

        index = -1
        for definition in definitions:
            index += 1
            if definition.type == BLOCK_TYPE_DUMMY:
                continue

            block = Block(buffer,
                          index,
                          definition.offset,
                          definition.offset + definition.length_bytes - 1,
                          definition.type)

            result.append(block)

        return result

    def find_spectra(self, blocks: List[Block]) -> List[Spectrum]:
        """
        Locates and returns the spectra.

        :param blocks:  The blocks.
        :return:        The spectra.
        """
        # HFL block?
        hfl = None
        for block in blocks:
            if block.name == "HFL":
                hfl = block

        # DPF blocks
        dpf = []
        for block in blocks:
            if block.name == "DPF":
                dpf.append(block)

        # Get corresponding data blocks
        data = []
        tmp = []
        for d in dpf:
            type_ = d.type - BLOCK_TYPE_INCREMENT_DATA_TO_DPF
            for block in blocks:
                if block.type == type_:
                    data.append(block)
                    tmp.append(d)
        dpf = tmp  # throw out DPF blocks that don't have a matching data block

        if len(dpf) != len(data):
            self.logger.critical(f"Can't read data, due to differing number of DPF blocks and "
                                 f"data blocks: {len(dpf)} != {len(data)}")
            for block in dpf:
                self.logger.info(str(block))
            for block in data:
                self.logger.info(str(block))

            return []

        result = []
        for i in range(len(dpf)):
            masked = data[i].type & BLOCK_TYPE_SPEC_MASK
            load = self.all_spectra or self.spectrum_block_type == to_hex_string(masked)

            if not load:
                continue

            num_points = dpf[i].get_from_id(NPT, 8, get_int)
            first_x = dpf[i].get_from_id(FXV, 8, get_double)
            last_x = dpf[i].get_from_id(LXV, 8, get_double)
            scale = dpf[i].get_from_id(CSF, 8, get_double)
            diff = (last_x - first_x) / (num_points - 1)

            self.logger.info(f"firstX={first_x}, lastX={last_x}, numPoints={num_points}, diff={diff}, scale={scale}")

            sd = {
                FIELD_OPUS_FIRST_X: first_x,
                FIELD_OPUS_LAST_X: last_x,
                FIELD_OPUS_NUM_POINTS: num_points,
                FIELD_OPUS_DIFF: diff,
                FIELD_OPUS_SCALE: scale,
                FIELD_OPUS_BLOCK_TYPE_DPF: to_hex_string(data[i].type),
                FIELD_OPUS_BLOCK_TYPE_HEX: to_hex_string(data[i].type & BLOCK_TYPE_SPEC_MASK)
            }

            if hfl is not None:
                instrument = hfl.get_from_id(INS, 8, get_text)
                if instrument is not None and instrument != "":
                    sd["Instrument"] = instrument

            waves = [first_x + n * diff for n in range(num_points)]
            ampls = [data[i].get(n * 4, get_float) * scale for n in range(num_points)]

            result.append(Spectrum(waves=waves, amplitudes=ampls, sample_data=sd))

        # Retrieve log
        text = ""
        for i, block in enumerate(blocks):
            if block.type == BLOCK_TYPE_TEXT:
                text += block.get_buffer().decode("ascii").strip()
        log = text.split("\0")
        log = [entry.strip() for entry in log]
        log = [entry for entry in log if entry != ""]
        self.logger.debug("\n".join(log))

        # Extract command lines
        cmdlines = []
        for i, entry in enumerate(log):
            if KEYWORD_CMDLINE in entry:
                cmdline = CommandLineData(entry)
                cmdlines.append(cmdline)
                self.logger.debug(str(cmdline))

        # Add sample-id and metadata
        for spectrum in result:
            for i, cmdline in enumerate(cmdlines):
                # Sample ID
                if cmdline.operation == self.operation:
                    if cmdline.has(self.key):
                        spectrum.id = cmdline.get(self.key)

                # Additional meta-data
                if cmdline.operation == self.operation or self.add_command_lines:
                    for key in cmdline.keys():
                        value = cmdline.get(key)
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                        index = "" if cmdline.operation == self.operation else f"{i + 1}."
                        spectrum.sample_data[f"{PREFIX_OPUS}{index}{cmdline.operation}.{cmdline.type}.{key}"] = value
            # Log
            if self.add_log:
                spectrum.sample_data[FIELD_OPUS_LOG] = "\n".join(log)

        return result

    @classmethod
    def get_writer_class(cls) -> 'Type[SpectrumWriter]':
        raise NotImplementedError(Reader.get_writer_class.__qualname__)

    def binary_mode(self, filename: str) -> bool:
        return True


read = Reader.read
