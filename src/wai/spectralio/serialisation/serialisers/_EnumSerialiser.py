from enum import IntEnum
from typing import TypeVar, IO, Type, Optional

from ...typing import TypeVarProperty
from ..error import WrongTypeError, SerialisationError
from .._Serialiser import Serialiser
from ._IntSerialiser import IntSerialiser

# The type of enum this serialiser serialises
EnumType = TypeVar("EnumType", bound=IntEnum)


class EnumSerialiser(Serialiser[EnumType]):
    """
    Serialiser which consumes integers as enumerations.
    """
    _enum_type: Type[EnumType] = TypeVarProperty(EnumType)
    _int_serialiser: Serialiser[int]

    def _check(self, obj: EnumType):
        WrongTypeError.check(obj, self._enum_type)

    def _serialise(self, obj: EnumType, stream: IO[bytes]):
        self._int_serialiser.serialise(obj.value, stream)

    def _deserialise(self, stream: IO[bytes]) -> EnumType:
        return self._enum_type(self._int_serialiser.deserialise(stream))

    @classmethod
    def for_enum(cls,
                 enum_type: Type[EnumType],
                 int_serialiser: Optional[Serialiser[int]] = None) -> 'EnumSerialiser[EnumType]':
        """
        Creates a serialiser for the given enum type.

        :param enum_type:       The enum type.
        :param int_serialiser:  The int serialiser to use under the hood, or
                                None to create a suitable one.
        :return:                The enum serialiser.
        """
        # Create the class
        class EnumTypeSerialiser(EnumSerialiser[enum_type], int_serialiser=int_serialiser):
            pass

        return EnumTypeSerialiser()

    def __init_subclass__(cls, *args, int_serialiser: Optional[Serialiser[int]] = None, **kwargs):
        # If the int_serialiser is supplied, save it
        if int_serialiser is not None:
            # Check it's suitable for the enum
            try:
                for value in cls._enum_type:
                    int_serialiser.serialise_to_bytes(value)
            except Exception as e:
                raise SerialisationError(f"Int serialiser unsuitable for enumeration: {e}") from e

            cls._int_serialiser = int_serialiser

        # Otherwise try to determine a suitable one
        else:
            # Get the minimum and maximum int representations
            min_value: int = min((val for val in cls._enum_type), key=lambda val: val.value)
            max_value: int = max((val for val in cls._enum_type), key=lambda val: val.value)

            # Work out if we need a signed field
            signed = min_value < 0 or max_value < 0

            # Get the number of bits/bytes required at most to represent all values
            bits_required = max(IntSerialiser.bit_length_actual(min_value, signed),
                                IntSerialiser.bit_length_actual(max_value, signed))
            bytes_required = bits_required // 8 + (1 if bits_required % 8 != 0 else 0)

            # Create an int serialiser to specification
            cls._int_serialiser = IntSerialiser(num_bytes=bytes_required, signed=signed)

        super().__init_subclass__(*args, **kwargs)
