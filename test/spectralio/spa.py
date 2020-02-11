import os

from wai.spectralio.spa import Reader

from .base import SpectrumReaderTest


class SPAReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "cylohex.spa")
