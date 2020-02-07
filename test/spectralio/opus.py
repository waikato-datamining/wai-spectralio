import os

from wai.spectralio.opus import Reader

from .base import SpectrumReaderTest


class OPUSReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "141009_001-01_0-6.0")
