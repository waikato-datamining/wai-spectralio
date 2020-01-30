import gzip
import logging
from typing import AnyStr, IO, Type

from .options import OptionHandler, Option
from .util import instanceoptionalmethod, dynamic_default


class Spectrum(object):
    """
    Simple container for spectral and sample data.
    """
    @dynamic_default(list, "waves")
    @dynamic_default(list, "ampls")
    @dynamic_default(dict, "sampledata")
    def __init__(self, id="noid", waves=None, ampls=None, sampledata=None):
        """
        Initializes the spectrum.

        :param id: the sample ID
        :type id: str
        :param waves: the wave numbers, list of floats
        :type waves: list
        :param ampls: the amplitudes, list of floats
        :type ampls: list
        :param sampledata: the sample data, dictionary with string keys
        :type sampledata: dict
        :param options: the options for the
        :type options: dict
        """

        if len(waves) != len(ampls):
            raise Exception("Lists with wave numbers and amplitudes must have same length: "
                            + str(len(waves)) + " != " + str(len(ampls)))

        self._id = id
        self._waves = waves[:]
        self._ampls = ampls[:]
        self._sampledata = sampledata.copy()

    @property
    def id(self):
        """
        Returns the sample id.

        :return: the sample id
        :rtype: str
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
    def waves(self):
        """
        Returns the wave numbers.

        :return: the wave numbers, list of floats
        :rtype: list
        """

        return self._waves

    @property
    def amplitudes(self):
        """
        Returns the amplitudes.

        :return: the amplitudes, list of floats
        :rtype: list
        """

        return self._ampls

    @property
    def sampledata(self):
        """
        Returns the sample data.

        :return: the sample data, dictionary with string keys
        :rtype: dict
        """

        return self._sampledata

    def __len__(self):
        """
        Returns the number of spectral points in this spectrum.

        :return: the number of waves/amplitudes
        :rtype: int
        """

        return len(self._waves)

    def __str__(self):
        """
        Returns a string representation of the spectrum.

        :return: the representation
        :rtype: str
        """

        return self.id + ": #points=" + str(len(self))


class LoggingObject:
    """
    Mixin class for adding logging to objects.
    """
    @property
    def logger(self) -> logging.Logger:
        cls = type(self)
        return logging.getLogger(cls.__module__ + "." + cls.__name__)


class SpectrumIOBase(OptionHandler, LoggingObject):
    """
    Base class for spectrum readers and writers.
    """
    # Debug option
    debug = Option(action='store_true', help='whether to turn debugging output on')

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


class SpectrumReader(SpectrumIOBase):
    """
    Ancestor for spectrum readers.
    """

    # Options
    instrument = Option(type=str, help='the instrument name', default="unknown")
    format = Option(type=str, help='the format type', default="NIR")
    keep_format = Option(action='store_true', help='whether to not override the format obtained from the file')

    @instanceoptionalmethod
    def read(self, fname, options=None):
        """
        Reads the spectra from the specified file.

        :param fname: the file to read
        :type fname: str
        :param options: the options to use
        :type options: dict
        :return: the list of spectra
        :rtype: list
        """
        # If called by class, create an instance
        if not instanceoptionalmethod.is_instance(self):
            return instanceoptionalmethod.type(self)(options).read(fname)

        # Apply the override options if given
        old_options = self.options
        if options is not None:
            self.options = options

        try:
            with self.open(fname, 'r') as specfile:
                return self._read(specfile, fname)
        finally:
            if options is not None:
                self.options = old_options

    def _read(self, specfile, fname):
        """
        Reads the spectra from the file handle.

        :param specfile: the file handle to read from
        :type specfile: file
        :param fname: the file being read
        :type fname: str
        :return: the list of spectra
        :rtype: list
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


class SpectrumWriter(SpectrumIOBase):
    """
    Ancestor for spectrum readers.
    """
    @instanceoptionalmethod
    def write(self, spectra, fname, options=None):
        """
        Writes the spectra to the specified file.

        :param spectra: the list of spectra
        :type spectra: list
        :param fname: the file to write to
        :type fname: str
        :param options: the options to use
        :type options: dict
        """
        # If called by class, create an instance
        if not instanceoptionalmethod.is_instance(self):
            return instanceoptionalmethod.type(self)(options).write(spectra, fname)

        # Apply the override options if given
        old_options = self.options
        if options is not None:
            self.options = options

        try:
            with self.open(fname, 'w') as specfile:
                return self._write(spectra, specfile, self.binary_mode(fname))
        finally:
            if options is not None:
                self.options = old_options

    def _write(self, spectra, specfile, as_bytes):
        """
        Writes the spectra to the filehandle.

        :param spectra: the list of spectra
        :type spectra: list
        :param specfile: the file handle to use
        :type specfile: file
        :param as_bytes: whether to write as bytes or string
        :type as_bytes: bool
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
