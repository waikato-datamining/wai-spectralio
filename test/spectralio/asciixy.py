import os
from wai.spectralio.asciixy import Reader, Writer

from .base import SpectrumReaderTest, SpectrumWriterTest


class ASCIIXYReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "1382928.txt")


class ASCIIXYWriterTest(SpectrumWriterTest):
    @classmethod
    def subject_type(cls):
        return Writer

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "1382928.txt")
