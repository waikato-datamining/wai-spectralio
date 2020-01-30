import os
from wai.spectralio.asc import Reader, Writer

from .base import SpectrumReaderTest, SpectrumWriterTest


class ASCReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "146048-NIR-FOSS.asc")


class ASCWriterTest(SpectrumWriterTest):
    @classmethod
    def subject_type(cls):
        return Writer

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "146048-NIR-FOSS.asc")
