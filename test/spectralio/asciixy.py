import os
from io import StringIO
from typing import Tuple, Type, Dict

from wai.test import AbstractTest
from wai.test.decorators import RegressionTest
from wai.test.serialisation import RegressionSerialiser

from wai.spectralio.api import Spectrum
from wai.spectralio.asciixy import Reader, Writer

from .serialisation import SpectrumSerialiser, TextFileSerialiser


class ReaderTest(AbstractTest):
    @classmethod
    def subject_type(cls):
        return Reader

    def common_resources(cls) -> Tuple[str]:
        return os.path.join("resources", "data", "1382928.txt"),

    def common_serialisers(cls) -> Dict[Type, Type[RegressionSerialiser]]:
        return {Spectrum: SpectrumSerialiser}

    @RegressionTest
    def read_file(self, subject: Reader, filename: str):
        return {"read": subject.read(filename)[0]}


class WriterTest(AbstractTest):
    @classmethod
    def subject_type(cls):
        return Writer

    def common_resources(cls) -> Tuple[str]:
        return os.path.join("resources", "data", "1382928.txt"),

    def common_serialisers(cls) -> Dict[Type, Type[RegressionSerialiser]]:
        return {StringIO: TextFileSerialiser}

    @RegressionTest
    def write_file(self, subject: Writer, filename: str):
        spec = Reader().read(filename)

        mem_file = StringIO()
        subject._write(spec, mem_file)

        return {"write": mem_file}
