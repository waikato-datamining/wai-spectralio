from enum import IntEnum
from typing import TypeVar, IO, Type, Optional

from ..error import WrongTypeError, SerialisationError
from .._Serialiser import Serialiser
from ._IntSerialiser import IntSerialiser

# The type of enum this serialiser serialises
EnumType = TypeVar("EnumType", bound=IntEnum)


class EnumSerialiser(Serialiser[EnumType]):
    """
    Serialiser which consumes integers as enumerations.
    """
    def __init__(self,
                 enum_type: Type[EnumType],
                 int_serialiser: Optional[Serialiser[int]] = None):
        # Check the int serialiser for suitability if given
        if int_serialiser is not None:
            self._check_int_serialiser(enum_type, int_serialiser)

        self._enum_type: Type[EnumType] = enum_type
        self._int_serialiser: Serialiser[int] = int_serialiser if int_serialiser is not None \
            else self._create_int_serialiser(enum_type)

    @staticmethod
    def _check_int_serialiser(enum_type: Type[EnumType], int_serialiser: Serialiser[int]):
        """
        Checks that the given int serialiser can handle serialisation
        of all values in the given enumeration.

        :param enum_type:       The enumeration.
        :param int_serialiser:  The int serialiser.
        """
        try:
            for value in enum_type:
                int_serialiser.serialise_to_bytes(value)
        except Exception as e:
            raise SerialisationError(f"Int serialiser unsuitable for enumeration: {e}") from e

    @staticmethod
    def _create_int_serialiser(enum_type: Type[EnumType]) -> IntSerialiser:
        """
        Creates an int serialiser suitable for the given enumeration.

        :param enum_type:   The enumeration.
        :return:            The int serialiser.
        """
        # Get the minimum and maximum int representations
        min_value: int = min(enum_type, key=lambda val: val.value)
        max_value: int = max(enum_type, key=lambda val: val.value)

        # Work out if we need a signed field
        signed = min_value < 0 or max_value < 0

        # Get the number of bits/bytes required at most to represent all values
        bits_required = max(IntSerialiser.bit_length_actual(min_value, signed),
                            IntSerialiser.bit_length_actual(max_value, signed))
        bytes_required = bits_required // 8 + (1 if bits_required % 8 != 0 else 0)

        # Create an int serialiser to specification
        return IntSerialiser(num_bytes=bytes_required, signed=signed)

    def _check(self, obj: EnumType):
        WrongTypeError.check(obj, self._enum_type)

    def _serialise(self, obj: EnumType, stream: IO[bytes]):
        self._int_serialiser.serialise(obj.value, stream)

    def _deserialise(self, stream: IO[bytes]) -> EnumType:
        return self._enum_type(self._int_serialiser.deserialise(stream))
