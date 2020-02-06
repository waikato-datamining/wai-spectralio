import os
from wai.spectralio.dpt import Reader, Writer

from .base import SpectrumReaderTest, SpectrumWriterTest


class DPTReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "sample.dpt")


class DPTWriterTest(SpectrumWriterTest):
    @classmethod
    def subject_type(cls):
        return Writer

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "sample.dpt")
