from io import StringIO, BytesIO
from typing import Tuple, Type, Dict, Optional, Any

from wai.test import AbstractTest
from wai.test.decorators import RegressionTest, Test
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
        return {f"read-{i}": spectrum for i, spectrum in enumerate(subject.read(filename))}


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

    @Test
    def round_trip(self, subject: SpectrumWriter, filename: str):
        """
        Tests that the writer writes what the reader reads.

        :param subject:     The writer.
        :param filename:    The example file.
        """
        # Get a corresponding reader
        reader = subject.get_reader()

        # Read the file
        spectra = reader.read(filename)

        # Write the spectra to memory
        binary_mode = subject.binary_mode(filename)
        mem_file = (BytesIO if binary_mode else StringIO)()
        subject._write(spectra, mem_file, binary_mode)

        # Re-read the written file
        mem_file.seek(0)
        round_trip_spectra = reader._read(mem_file, filename)

        for spectrum, round_trip_spectrum in zip(spectra, round_trip_spectra):
            error = SpectrumSerialiser.compare(spectrum, round_trip_spectrum)
            self.assertTrue(error is None, error)
