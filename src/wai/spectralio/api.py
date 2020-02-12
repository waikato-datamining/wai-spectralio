import gzip
import logging
from abc import ABC, abstractmethod
from typing import AnyStr, IO, Type, Optional, List, Dict, Any

from .options import OptionHandler, Option
from .util import instanceoptionalmethod
from .util.dynamic_defaults import dynamic_default, with_dynamic_defaults


class Spectrum:
    """
    Simple container for spectral and sample data.
    """
    @with_dynamic_defaults
    def __init__(self,
                 sample_id: str = "noid",
                 waves: List[float] = dynamic_default(list),
                 amplitudes: List[float] = dynamic_default(list),
                 sample_data: Dict[str, Any] = dynamic_default(dict)):
        """
        Initializes the spectrum.

        :param sample_id:       The sample ID.
        :param waves:           The wave numbers.
        :param amplitudes:      The amplitudes.
        :param sample_data:     The sample data.
        """
        # Make sure the number of wave-numbers matches the number of amplitudes
        if len(waves) != len(amplitudes):
            raise Exception("Lists with wave numbers and amplitudes must have same length: "
                            + str(len(waves)) + " != " + str(len(amplitudes)))

        self._id: str = sample_id
        self._waves: List[float] = waves[:]
        self._amplitudes: List[float] = amplitudes[:]
        self._sample_data: Dict[str, Any] = sample_data.copy()

    @property
    def id(self) -> str:
        """
        Returns the sample id.

        :return:    The sample id.
        """
        return self._id

    @id.setter
    def id(self, value: str):
        """
        Sets the sample ID.

        :param value:   The new sample ID.
        """
        self._id = value

    @property
    def waves(self) -> List[float]:
        """
        Returns the wave numbers.

        :return:    The wave numbers.
        """
        return self._waves

    @property
    def amplitudes(self) -> List[float]:
        """
        Returns the amplitudes.

        :return:    The amplitudes.
        """
        return self._amplitudes

    @property
    def sample_data(self) -> Dict[str, Any]:
        """
        Returns the sample data.

        :return:    The sample data.
        """
        return self._sample_data

    def __len__(self) -> int:
        """
        Returns the number of spectral points in this spectrum.

        :return:    The number of waves/amplitudes.
        """
        return len(self._waves)

    def __str__(self) -> str:
        """
        Returns a string representation of the spectrum.

        :return:    The representation.
        """
        return self.id + ": #points=" + str(len(self))


class LoggingObject:
    """
    Mixin class for adding logging to objects.
    """
    @property
    def logger(self) -> logging.Logger:
        """
        Gets the logger for this class.

        :return:    The logger.
        """
        cls = type(self)
        return logging.getLogger(cls.__module__ + "." + cls.__name__)


class SpectrumIOBase(OptionHandler, LoggingObject, ABC):
    """
    Base class for spectrum readers and writers.
    """
    # Debug option
    debug = Option(action='store_true', help='whether to turn debugging output on')

    @abstractmethod
    def binary_mode(self, filename: str) -> bool:
        """
        Whether the file should be accessed in binary mode.

        :param filename:    The name of the file.
        :return:            True if it should be accessed in binary mode,
                            False if not.
        """
        raise NotImplementedError(SpectrumIOBase.binary_mode.__qualname__)

    def open(self, filename: str, mode: str) -> IO[AnyStr]:
        """
        Opens the given file in the given mode.

        :param filename:    The file to open.
        :param mode:        'r' for read or 'w' for write.
        :return:            The file handle.
        """
        # Make sure mode is either 'r' or 'w'
        if mode not in {'r', 'w', 'R', 'W'}:
            raise ValueError(f"Mode must be 'r' or 'w', not '{mode}'")
        mode = mode.lower()

        if filename.endswith(".gz"):
            mode = mode if self.binary_mode(filename) else f"{mode}t"
            return gzip.open(filename, mode)
        else:
            mode = f"{mode}b" if self.binary_mode(filename) else mode
            return open(filename, mode)


class SpectrumReader(SpectrumIOBase, ABC):
    """
    Ancestor for spectrum readers.
    """
    # Options
    instrument = Option(type=str, help='the instrument name', default="unknown")
    format = Option(type=str, help='the format type', default="NIR")
    keep_format = Option(action='store_true', help='whether to not override the format obtained from the file')

    @instanceoptionalmethod
    def read(self, filename: str, options: Optional[List[str]] = None) -> List[Spectrum]:
        """
        Reads the spectra from the specified file.

        :param filename:    The file to read.
        :param options:     The options to use.
        :return:            A list of spectra in the file.
        """
        # If called by class, create an instance
        if not instanceoptionalmethod.is_instance(self):
            return instanceoptionalmethod.type(self)(options).read(filename)

        # Save the current options
        old_options = self.options

        try:
            # Apply the override options if given
            if options is not None:
                self.options = options

            with self.open(filename, 'r') as spec_file:
                return self._read(spec_file, filename)
        finally:
            if options is not None:
                self.options = old_options

    def _read(self, spec_file: IO[AnyStr], filename: str) -> List[Spectrum]:
        """
        Reads the spectra from the file handle.

        :param spec_file:   The file handle to read from.
        :param filename:    The file being read.
        :return:            A list of spectra in the file.
        """
        raise NotImplementedError(SpectrumReader._read.__qualname__)

    @classmethod
    def get_writer_class(cls) -> 'Type[SpectrumWriter]':
        """
        Gets the writer class that writes the same file-type as
        this reader class reads.

        :return:    The writer.
        """
        raise NotImplementedError(SpectrumReader.get_writer_class.__qualname__)

    def get_writer(self) -> 'SpectrumWriter':
        """
        Gets a writer that writes the same format as this reader
        reads. Any common options between the reader and writer are
        copied.

        :return:    The writer.
        """
        # Get the writer class
        writer_class = self.get_writer_class()

        # Get the common options between ourselves and the writer class
        common_options = self.get_common_options(writer_class)

        # Get the options sub-list corresponding to those options
        common_option_sub_list = self.get_options_sub_list(common_options)

        return writer_class(common_option_sub_list)


class SpectrumWriter(SpectrumIOBase, ABC):
    """
    Ancestor for spectrum readers.
    """
    @instanceoptionalmethod
    def write(self, spectra: List[Spectrum], filename: str, options: Optional[List[str]] = None):
        """
        Writes the spectra to the specified file.

        :param spectra:     The list of spectra.
        :param filename:    The file to write to.
        :param options:     The options to use.
        """
        # If called by class, create an instance
        if not instanceoptionalmethod.is_instance(self):
            return instanceoptionalmethod.type(self)(options).write(spectra, filename)

        # Save the current options
        old_options = self.options

        try:
            # Apply the override options if given
            if options is not None:
                self.options = options

            with self.open(filename, 'w') as spec_file:
                return self._write(spectra, spec_file, self.binary_mode(filename))
        finally:
            if options is not None:
                self.options = old_options

    def _write(self, spectra: List[Spectrum], spec_file: IO[AnyStr], as_bytes: bool):
        """
        Writes the spectra to the file-handle.

        :param spectra:     The list of spectra.
        :param spec_file:    The file handle to write to.
        :param as_bytes:    Whether to write as bytes or string.
        """
        raise NotImplementedError(SpectrumWriter._write.__qualname__)

    @classmethod
    def get_reader_class(cls) -> Type[SpectrumReader]:
        """
        Gets the reader class that reads the same file-type as
        this writer class writes.

        :return:    The reader class.
        """
        raise NotImplementedError(SpectrumWriter.get_reader_class.__qualname__)

    def get_reader(self) -> SpectrumReader:
        """
        Gets a reader that reads the same format as this writer
        writes. Any common options between the reader and writer are
        copied.

        :return:    The reader.
        """
        # Get the reader class
        reader_class = self.get_reader_class()

        # Get the common options between ourselves and the reader class
        common_options = self.get_common_options(reader_class)

        # Get the options sub-list corresponding to those options
        common_option_sub_list = self.get_options_sub_list(common_options)

        return reader_class(common_option_sub_list)
