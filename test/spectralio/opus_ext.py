import os
from typing import Optional, Tuple, Any, Dict

from wai.spectralio.opus_ext import Reader

from .base import SpectrumReaderTest


class OPUSExtReaderTest(SpectrumReaderTest):
    @classmethod
    def subject_type(cls):
        return Reader

    def common_arguments(cls) -> Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]]:
        return tuple(), {
            "options": ["--all-spectra"]
        }

    @classmethod
    def get_example_filename(cls) -> str:
        return os.path.join("resources", "data", "141009_001-01_0-6.0")
