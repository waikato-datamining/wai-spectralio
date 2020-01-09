class Spectrum(object):
    """
    Simple container for spectral and meta data.
    """

    def __init__(self, id, waves, ampls, meta):
        """
        Initializes the spectrum.

        :param id: the sample ID
        :type id: str
        :param waves: the wave numbers, list of floats
        :type waves: list
        :param ampls: the amplitudes, list of floats
        :type ampls: list
        :param meta: the meta-data, dictionary with string keys
        :type meta: dict
        """

        if len(waves) != len(ampls):
            raise Exception("Lists with wave numbers and amplitudes must have same length: "
                            + str(len(waves)) + " != " + str(len(ampls)))

        self._id = id
        self._waves = waves[:]
        self._ampls = ampls[:]
        self._meta = meta.copy()

    def id(self):
        """
        Returns the sample id.

        :return: the sample id
        :rtype: str
        """

        return self._id

    def waves(self):
        """
        Returns the wave numbers.

        :return: the wave numbers, list of floats
        :rtype: list
        """

        return self._waves

    def amplitudes(self):
        """
        Returns the amplitudes.

        :return: the amplitudes, list of floats
        :rtype: list
        """

        return self._ampls

    def metadata(self):
        """
        Returns the meta-data.

        :return: the meta-data, dictionary with string keys
        :rtype: dict
        """

        return self._meta

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

        return self.id() + ": #points=" + str(len(self))


class SpectrumReader(object):
    """
    Ancestor for spectrum readers.
    """

    def read(self, fname):
        """
        Reads the spectra from the specified file.

        :param fname: the file to read
        :type fname: str
        :return: the list of spectra
        :rtype: list
        """

        raise NotImplemented()


class SpectrumWriter(object):
    """
    Ancestor for spectrum readers.
    """

    def write(self, spectra, fname):
        """
        Writes the spectra to the specified file.

        :param spectra: the list of spectra
        :type spectra: list
        :param fname: the file to write to
        :type fname: str
        """

        raise NotImplemented()
