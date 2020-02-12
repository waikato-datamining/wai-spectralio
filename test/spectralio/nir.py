import os
from typing import Optional, Tuple, Any, Dict

from wai.spectralio.nir import Reader, Writer

from .base import SpectrumReaderTest, SpectrumWriterTest


class NIRReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "VALK10.NIR")


class NIRWriterTest(SpectrumWriterTest):
    @classmethod
    def subject_type(cls):
        return Writer

    @classmethod
    def common_arguments(cls) -> Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]]:
        # FIXME: Add timestamp argument as default timestamp uses today's
        #        date, which means the regression fails after one day.
        return tuple(), dict()


    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "VALK10.NIR")
