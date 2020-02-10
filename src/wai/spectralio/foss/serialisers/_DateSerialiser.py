import datetime
from typing import IO

from ...serialisation import Serialiser


class DateSerialiser(Serialiser[datetime.date]):
    """
    Serialiser which stores a date.

    Format is:

    Least Significant Byte (MMMDDDDD)
    Most Significant Byte  (YYYYYYYM)

    Year is: years since 1980.
    """
    def _check(self, obj: datetime.date):
        # Make sure it really is a date
        if not isinstance(obj, datetime.date):
            raise TypeError(f"obj is not a date ({type(obj).__name__})")

    def _serialise(self, obj: datetime.date, stream: IO[bytes]):
        # Get the day, month and year
        year = obj.year - 1980
        month = obj.month
        day = obj.day

        # Pack them into a 2-byte int
        combined = (year << 9) + (month << 5) + day

        # Write the int
        stream.write(combined.to_bytes(2, "little", signed=False))

    def _deserialise(self, stream: IO[bytes]) -> datetime.date:
        # Read 2 bytes
        bytes = stream.read(2)

        # If zeroes, return the epoch
        if bytes == b'\x00\x00':
            return datetime.date(1980, 1, 1)

        # Convert them into the packed-int format
        combined = int.from_bytes(bytes, "little", signed=False)

        # Extract the day, month and year
        day = combined & 0x1F
        month = (combined >> 5) & 0xF
        year = (combined >> 9) + 1980

        return datetime.date(year, month, day)
