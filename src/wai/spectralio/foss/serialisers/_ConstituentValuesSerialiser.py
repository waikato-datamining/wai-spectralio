from typing import IO

from ...api import LoggingObject
from ...serialisation import Serialiser
from ...serialisation.serialisers import FloatSerialiser
from .._ConstituentValues import ConstituentValues


class ConstituentValuesSerialiser(LoggingObject, Serialiser[ConstituentValues]):
    """
    Serialiser of constituent values.
    """
    PAD_VALUE: bytes = b'\x00' * 4

    def __init__(self):
        self._float_serialiser: FloatSerialiser = FloatSerialiser(double_precision=False)

    def _check(self, obj: ConstituentValues):
        # Make sure the object really is a constituent values object.
        if not isinstance(obj, ConstituentValues):
            raise TypeError("obj is not a ConstituentValues")

    def _serialise(self, obj: ConstituentValues, stream: IO[bytes]):
        # Check the number of constituents
        num_constituents = len(obj.constituents)
        if num_constituents > 32:
            self.logger.warning(f"More than 32 constituents specified ({num_constituents}). "
                                f"Using 32")

        for constituent in obj.constituents[:32]:
            self._float_serialiser.serialise(constituent, stream)

        # Zero-pad if fewer than 32 constituents
        while num_constituents < 32:
            stream.write(self.PAD_VALUE)
            num_constituents += 1

    def _deserialise(self, stream: IO[bytes]) -> ConstituentValues:
        cv = ConstituentValues()

        while len(cv.constituents) < 32:
            # Read 4 bytes
            buffer = stream.read(4)

            # If the bytes are padding, we're done
            if buffer == self.PAD_VALUE:
                break

            cv.constituents.append(self._float_serialiser.deserialise_from_bytes(buffer))

        # Consume any additional padding
        if len(cv.constituents) != 32:
            # 31 not 32 because we've already consumed one word to determine
            # that we've hit padding above
            stream.read(len(self.PAD_VALUE) * (31 - len(cv.constituents)))

        return cv
