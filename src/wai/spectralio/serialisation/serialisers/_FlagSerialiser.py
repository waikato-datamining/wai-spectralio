from typing import Tuple, IO, Type, Iterator, Dict, List, Union
import keyword

from .._Serialiser import Serialiser

# Flag name specifying that the bit is unused
UNUSED: str = ""


class Flags:
    """
    Class specifying the parsed flags. Immutable.
    """
    # The parent flag serialiser for this flags type.
    _parent: 'FlagSerialiser'

    def __init__(self, *flags: bool, **keyword_flags: bool):
        # Make sure all keyword flags have valid names
        for name in keyword_flags:
            if not self._parent.has_flag(name):
                raise NameError(f"Invalid flag name '{name}'")

        # Make sure there aren't too many positional flags
        if len(flags) > self._parent.num_flags:
            raise IndexError(f"Received {len(flags)} positional flag values but expected "
                             f"at most {self._parent.num_flags}")

        # Make sure no flag is specified by position and name
        max_position_exclusive: int = self._parent.num_flags - len(flags)
        for flag in keyword_flags:
            if self._parent.bit_position(flag) >= max_position_exclusive:
                raise RuntimeError(f"Flag '{flag}' specified by name and position")

        # Save the values
        self._values: List[bool] = list(flags)
        if max_position_exclusive > 0:
            self._values += [False] * max_position_exclusive
            for name, value in keyword_flags.items():
                index: int = self._internal_index(name)
                self._values[index] = value

    def _internal_index(self, flag: Union[str, int]) -> int:
        """
        Gets the index of the flag in the value list.

        :param flag:    The flag, by name or bit-position.
        :return:        The index of the flag's value in the value list.
        """
        # Convert names to bit positions
        if isinstance(flag, str):
            flag = self._parent.bit_position(flag)

        # Make sure the bit-position is in range
        if not (0 <= flag < self._parent.num_flags):
            raise ValueError(f"Flag bit-position {flag} is out of range "
                             f"[0,{self._parent.num_flags})")

        return self._parent.num_flags - flag - 1

    def __getitem__(self, item: Union[str, int]):
        return self._values[self._internal_index(item)]

    def __getattr__(self, item: str):
        if self._parent.has_flag(item):
            return self[item]

        raise AttributeError(item)

    def enumerate(self) -> Iterator[Tuple[int, bool]]:
        """
        Enumerates the values of the flags by their bit-position.

        :return:    An iterator of bit-position, flag-value pairs.
        """
        return ((bit_position, self[bit_position])
                for bit_position in range(self._parent.num_flags))

    def __init_subclass__(cls, **kwargs):
        # Get the parent serialiser from kwargs
        if "parent" not in kwargs:
            raise KeyError(f"'parent' serialiser missing from class")
        cls._parent = kwargs.pop("parent")

        super().__init_subclass__(**kwargs)

    def __repr__(self):
        values = [f"{flag}={self[bit_position]}" for flag, bit_position in self._parent.flags()]
        return f"Flags({', '.join(values)})"


class FlagSerialiser(Serialiser[Flags]):
    """
    Serialiser which serialises a number of boolean flags to
    individual bits. The number of flags determines the number
    of bytes consumed, which is always a whole number i.e. the
    number of bits consumed is always a multiple of 8.
    """
    def __init__(self, *flags: str):
        # Make sure all flag names are valid
        self._check_flag_names(flags)

        # Save the required bit/byte lengths of the specification
        self._num_flags: int = len(flags)
        self._num_bytes: int = self._num_flags // 8 + (1 if self._num_flags % 8 != 0 else 0)

        # Save the flag names/positions
        self._flags: Dict[str, int] = {
            flag: self._num_flags - index - 1
            for index, flag in enumerate(flags)
            if flag != UNUSED
        }

        # Create the flag specification's type
        self._specification: Type[Flags] = self._create_specification()

    def flags(self) -> Iterator[Tuple[str, int]]:
        """
        Gets an iterator over the flags and their bit-positions.

        :return:    The iterator.
        """
        return ((flag, position) for flag, position in self._flags.items())

    def has_flag(self, name: str) -> bool:
        """
        Whether this serialiser has a flag with the given name.

        :param name:    The flag name.
        :return:        True if the flag exists.
        """
        return name in self._flags

    def bit_position(self, flag: str) -> int:
        """
        Gets the bit position of a flag by name.

        :param flag:    The flag name.
        :return:        The flag's bit position.
        """
        # Make sure the flag is valid
        if not self.has_flag(flag):
            raise NameError(f"Serialiser has no flag named '{flag}'")

        return self._flags[flag]

    @property
    def num_flags(self) -> int:
        """
        The number of flags (including unused bits) specified.

        :return:    The number of flags.
        """
        return self._num_flags

    @property
    def specification(self) -> Type[Flags]:
        """
        Gets the named-tuple type of this specification.

        :return:    The named-tuple type.
        """
        return self._specification

    def _check(self, obj: Flags):
        # Make sure the flags came from our specification
        if not isinstance(obj, self._specification):
            raise ValueError(f"Supplied flags are not from the serialiser's specification")

    def _serialise(self, obj: Flags, stream: IO[bytes]):
        # Create an integer to buffer the flags
        data_int: int = 0

        # Add each flag to the integer
        for bit_position, flag in obj.enumerate():
            if flag:
                data_int += 1 << bit_position

        # Write the int to stream
        stream.write(data_int.to_bytes(self._num_bytes, "big", signed=False))

    def _deserialise(self, stream: IO[bytes]) -> Flags:
        # Read the required bytes
        data = stream.read(self._num_bytes)

        # Make sure enough bytes were read
        if len(data) != self._num_bytes:
            raise RuntimeError(f"Failed to read enough data from stream "
                               f"(required {self._num_bytes} bytes, "
                               f"received {len(data)})")

        # Convert the bytes to an integer
        data_int: int = int.from_bytes(data, "big", signed=False)

        return self._specification(*((data_int >> bit_position) % 2 == 1
                                     for bit_position in reversed(range(self._num_flags))))

    @staticmethod
    def _check_flag_names(flag_names: Tuple[str, ...]):
        """
        Makes sure the flag names are valid.

        :param flag_names:  The flag names.
        """
        # Must supply at least one flag
        if len(flag_names) == 0:
            raise ValueError("No flag names supplied")

        # Keep track of names we've seen so we don't use them twice
        seen = set()

        # Process each flag name
        for flag_name in flag_names:
            # Reserved flag name for unused flags can be skipped
            if flag_name == UNUSED:
                continue

            # Make sure the name doesn't start with an underscore
            if flag_name.startswith("_"):
                raise ValueError(f"'{flag_name}' is not a valid flag-name "
                                 f"because it starts with an underscore")

            # Make sure the name isn't already used
            if flag_name in seen:
                raise ValueError(f"'{flag_name}' is specified more than once")

            # Make sure the name can be used as an identifier
            if not flag_name.isidentifier():
                raise ValueError(f"'{flag_name}' is not a valid flag name "
                                 f"(not a Python identifier)")

            # Make sure it's not a reserved identifier
            if keyword.iskeyword(flag_name):
                raise ValueError(f"'{flag_name}' is not a valid flag name "
                                 f"(reserved Python keyword)")

            # Add the name to the seen set
            seen.add(flag_name)

    def _create_specification(self) -> Type['Flags']:
        """
        Creates a sub-class of the Flags type specific to this
        serialiser.

        :return:    The Flags type.
        """
        # Create a sub-class of Flags for this serialiser
        class _Flags(Flags, parent=self):
            pass

        return _Flags
