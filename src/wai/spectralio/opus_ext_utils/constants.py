BLOCK_OFFSET: int = 36
"""The offset for block definitions in the header"""

HEADER_LENGTH: int = 500
"""Maximum length of header (made up value!)"""

BLOCK_DEFINITION_LENGTH: int = 12
"""The block definition length (type, length, offset)"""

BLOCK_TYPE_DUMMY: int = 0
"""The dummy block type (???)"""

BLOCK_TYPE_TEXT: int = 1080557568
"""The text block type"""

# FIXME: One of the below 2 comments is a copy/paste error

BLOCK_TYPE_SPEC_MASK: int = 0x000FFFFF
"""The mask for the block type of the main spectrum"""

BLOCK_TYPE_MAIN_MASK: int = 0x100F
"""The mask for the block type of the main spectrum"""

BLOCK_TYPE_INCREMENT_DATA_TO_DPF: int = 16
"""Increment from data to DPF block type"""

NPT: bytes = b'NPT\x00'
"""The NPT character sequence"""

FXV: bytes = b'FXV\x00'
"""The FXV character sequence"""

LXV: bytes = b'LXV\x00'
"""The LXV character sequence"""

CSF: bytes = b'CSF\x00'
"""The CSF character sequence"""

INS: bytes = b'INS\x00'
"""The INS character sequence"""

KEYWORD_CMDLINE = "COMMAND_LINE"
"""The command line keyword"""

OPERATION_MEASURE_SAMPLE: str = "MeasureSample"
"""The operation containing the sample ID"""

KEY_SAMPLE_ID_2: str = "SNM"
"""The key for the sample ID (2)"""
