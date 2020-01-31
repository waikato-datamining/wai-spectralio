from io import StringIO
from typing import Tuple, Type, Dict, Optional, Any

from wai.test import AbstractTest
from wai.test.decorators import RegressionTest
from wai.test.serialisation import RegressionSerialiser

from wai.spectralio.api import Spectrum, SpectrumReader, SpectrumWriter

from .serialisation import SpectrumSerialiser, TextFileSerialiser


class SpectrumReaderTest(AbstractTest):
    @classmethod
    def get_example_filename(cls) -> str:
        """
        Gets the name of the example file to use.

        :return:    The filename.
        """
        raise NotImplementedError(SpectrumReaderTest.get_example_filename.__qualname__)

    @classmethod
    def common_resources(cls) -> Optional[Tuple[Any, ...]]:
        return cls.get_example_filename(),

    @classmethod
    def common_serialisers(cls) -> Dict[Type, Type[RegressionSerialiser]]:
        return {Spectrum: SpectrumSerialiser}

    @RegressionTest
    def read(self, subject: SpectrumReader, filename: str):
        return {"read": subject.read(filename)[0]}


class SpectrumWriterTest(AbstractTest):
    @classmethod
    def get_example_filename(cls) -> str:
        """
        Gets the name of the example file to use.

        :return:    The filename.
        """
        raise NotImplementedError(SpectrumReaderTest.get_example_filename.__qualname__)

    @classmethod
    def common_resources(cls) -> Optional[Tuple[Any, ...]]:
        return cls.get_example_filename(),

    @classmethod
    def common_serialisers(cls) -> Dict[Type, Type[RegressionSerialiser]]:
        return {StringIO: TextFileSerialiser}

    @RegressionTest
    def write(self, subject: SpectrumWriter, filename: str):
        spec = subject.get_reader().read(filename)

        mem_file = StringIO()
        subject._write(spec, mem_file, False)

        return {"write": mem_file}
