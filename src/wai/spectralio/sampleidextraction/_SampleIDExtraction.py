import os
import re

from ..options import OptionHandler, Option


class SampleIDExtraction(OptionHandler):
    """
    Mixin for schemes that extract the sample ID from the filename.
    """
    # Options
    sample_id_extraction = Option(required=False,
                                  nargs=2,
                                  help='the scheme for extracting the sample ID from the filename')

    def _check(self, file: str):
        """
        Performs checks before the actual extraction.

        :param file:    The current file.
        """
        if file is None:
            raise ValueError("No file provided!")

    def _do_extract(self, file: str) -> str:
        """
        Performs the actual extraction.

        :param file:    The current file.
        :return:        The extracted sample ID.
        """
        extraction_option = self.sample_id_extraction

        if extraction_option is None:
            return self._filename(file)
        else:
            return self._regexp(file, *extraction_option)

    def _filename(self, file: str) -> str:
        """
        Performs filename extraction of the sample ID.

        :param file:    The current file.
        :return:        The extracted sample ID.
        """
        return os.path.splitext(os.path.basename(file))[0]

    def _regexp(self, file: str, regex: str, group: str):
        """
        Performs regular expression extraction of the sample ID.

        :param file:    The current file.
        :param regex:   The regular expression.
        :param group:   The group to extract the sample ID from.
        :return:        The extracted sample ID.
        """
        # Try to match the filename
        match = re.match(regex, file)

        # Attempt to parse integer group
        group_index = None
        try:
            group_index = int(group)
        except ValueError:
            pass

        return match.group(group_index if group_index is not None else group)

    def extract(self, file: str) -> str:
        """
        Performs the extraction.

        :param file:    The current file.
        :return:        The extracted sample ID.
        """
        self._check(file)
        return self._do_extract(file)
