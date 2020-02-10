from typing import List

from ..api import LoggingObject


class ConstituentValues(LoggingObject):
    """
    Constituent (or reference) values.
    """
    def __init__(self):
        self.constituents: List[float] = []
