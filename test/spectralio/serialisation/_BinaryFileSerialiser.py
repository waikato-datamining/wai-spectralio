from io import BytesIO
from typing import IO, Optional

from wai.test.serialisation import RegressionSerialiser


class BinaryFileSerialiser(RegressionSerialiser):
    @classmethod
    def binary(cls) -> bool:
        return True

    @classmethod
    def extension(cls) -> str:
        return "bin"

    @classmethod
    def serialise(cls, result: BytesIO, file: IO[bytes]):
        result.seek(0)
        file.write(result.read())

    @classmethod
    def deserialise(cls, file: IO[bytes]) -> BytesIO:
        result = BytesIO()
        result.write(file.read())
        return result

    @classmethod
    def compare(cls, result: BytesIO, reference: BytesIO) -> Optional[str]:
        result.seek(0)
        reference.seek(0)
        if result.read() != reference.read():
            return "Binary files don't match"

        return None
