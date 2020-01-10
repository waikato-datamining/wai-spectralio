import argparse


class Spectrum(object):
    """
    Simple container for spectral and sample data.
    """

    def __init__(self, id, waves, ampls, sampledata):
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


class OptionHandler(object):
    """
    Super class for option-handling classes.
    """

    def __init__(self, options=None):
        """
        Initializes the reader.

        :param options: the options to use
        :type options: dict
        """
        super(OptionHandler, self).__init__()
        self._options_parser = self._define_options()
        self._options_parsed = argparse.Namespace()
        self._options_list = None
        # now initialize options/namespace
        self.options = options

    def _define_options(self):
        """
        Configures the options parser.

        :return: the option parser
        :rtype: argparse.ArgumentParser
        """

        result = argparse.ArgumentParser(description=self.__class__.__module__ + "." + self.__class__.__name__)

        return result

    @property
    def options(self):
        """
        Returns the currently used options.

        :return: the list of options (strings)
        :rtype: list
        """
        return self._options_list

    @options.setter
    def options(self, options):
        """
        Sets the options to use.

        :param options: the list of options, can be None
        :type options: list
        """
        if (options is None) or (len(options) == 0):
            self._options_parsed = self._options_parser.parse_args([])
        else:
            self._options_parsed = self._options_parser.parse_args(options)
        self._options_list = ([] if options is None else options.copy())

    def options_help(self):
        """
        Returns the help for the options.

        :return: the help
        :rtype: str
        """
        return self._options_parser.format_help()


class SpectrumReader(OptionHandler):
    """
    Ancestor for spectrum readers.
    """

    def __init__(self, options=None):
        """
        Initializes the reader.

        :param options: the options to use
        :type options: dict
        """
        super(SpectrumReader, self).__init__(options=options)

    def _define_options(self):
        """
        Configures the options parser.

        :return: the option parser
        :rtype: argparse.ArgumentParser
        """

        result = super(SpectrumReader, self)._define_options()
        result.add_argument('--debug', action='store_true', help='whether to turn debugging output on')
        result.add_argument('--instrument', type=str, help='the instrument name', default="unknown")
        result.add_argument('--format', type=str, help='the format type', default="NIR")
        result.add_argument('--keep_format', action='store_true', help='whether to not override the format obtained from the file')

        return result

    def read(self, fname):
        """
        Reads the spectra from the specified file.

        :param fname: the file to read
        :type fname: str
        :return: the list of spectra
        :rtype: list
        """

        raise NotImplemented()


class SpectrumWriter(OptionHandler):
    """
    Ancestor for spectrum readers.
    """

    def __init__(self, options=None):
        """
        Initializes the reader.

        :param options: the options to use
        :type options: dict
        """
        super(SpectrumWriter, self).__init__(options=options)

    def _define_options(self):
        """
        Configures the options parser.

        :return: the option parser
        :rtype: argparse.ArgumentParser
        """

        result = super(SpectrumWriter, self)._define_options()
        result.add_argument('--debug', action='store_true', help='whether to turn debugging output on')

        return result

    def write(self, spectra, fname):
        """
        Writes the spectra to the specified file.

        :param spectra: the list of spectra
        :type spectra: list
        :param fname: the file to write to
        :type fname: str
        """

        raise NotImplemented()
