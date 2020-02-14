from typing import Any, Type

from ._SerialisationError import SerialisationError


class WrongTypeError(SerialisationError):
    """
    Class for trying to serialise the wrong value type.
    """
    def __init__(self, value: Any, expected_type: Type):
        super().__init__(f"Expected a {expected_type.__name__} "
                         f"but got a {type(value).__name__}")

    @classmethod
    def check(cls, value: Any, expected_type: Type):
        """
        Checks the value is the right type, or raises an instance
        of this error-type if not.

        :param value:           The value received.
        :param expected_type:   The expected type.
        """
        if not isinstance(value, expected_type):
            raise cls(value, expected_type)
