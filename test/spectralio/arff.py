import os
from wai.spectralio.asc import Reader, Writer

from .base import SpectrumReaderTest, SpectrumWriterTest


class ARFFReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "sample.arff")


class ARFFWriterTest(SpectrumWriterTest):
    @classmethod
    def subject_type(cls):
        return Writer

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "sample.arff")
