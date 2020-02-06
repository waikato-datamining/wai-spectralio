import os

from wai.spectralio.mps import Reader

from .base import SpectrumReaderTest


class MPSReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "1-Cl-V.mps")
