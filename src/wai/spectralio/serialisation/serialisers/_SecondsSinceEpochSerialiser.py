import datetime
from typing import IO

from .._Serialiser import Serialiser
from ._IntSerialiser import IntSerialiser


class SecondsSinceEpochSerialiser(Serialiser[datetime.datetime]):
    """
    Serialises a date/time as the number of seconds since a given epoch
    (as an integer).
    """
    def __init__(self,
                 epoch: datetime.datetime = datetime.datetime.fromtimestamp(0),
                 int_serialiser: Serialiser[int] = IntSerialiser()):
        self._epoch: datetime.datetime = epoch
        self._int_serialiser: Serialiser[int] = int_serialiser

    def _check(self, obj: datetime.datetime):
        # Make sure it really is a datetime
        if not isinstance(obj, datetime.datetime):
            raise TypeError(f"{SecondsSinceEpochSerialiser.__name__} serialises "
                            f"{datetime.datetime.__name__}s")

    def _serialise(self, obj: datetime.datetime, stream: IO[bytes]):
        # Get the number of seconds since the epoch
        num_seconds: int = int((obj - self._epoch).total_seconds())

        # Serialise it as an int
        self._int_serialiser.serialise(num_seconds, stream)

    def _deserialise(self, stream: IO[bytes]) -> datetime.datetime:
        # Deserialise the number of seconds since the epoch
        num_seconds: int = self._int_serialiser.deserialise(stream)

        # Convert to a time-delta
        time_delta = datetime.timedelta(seconds=float(num_seconds))

        return self._epoch + time_delta
