from io import StringIO
from typing import IO, Optional

from wai.test.serialisation import RegressionSerialiser


class TextFileSerialiser(RegressionSerialiser):
    @classmethod
    def binary(cls) -> bool:
        return False

    @classmethod
    def extension(cls) -> str:
        return "txt"

    @classmethod
    def serialise(cls, result: StringIO, file: IO[str]):
        result.seek(0)
        file.write(result.read())

    @classmethod
    def deserialise(cls, file: IO[str]) -> StringIO:
        result = StringIO()
        result.write(file.read())
        return result

    @classmethod
    def compare(cls, result: StringIO, reference: StringIO) -> Optional[str]:
        result.seek(0)
        reference.seek(0)
        def line_counter():
            i = 0
            while True:
                i = i + 1
                yield i
        for line_no, result_line, reference_line in zip(line_counter(), result, reference):
            if result_line != reference_line:
                return f"Mismatch at line {line_no}: '{result_line[:-1]}' instead of '{reference_line[:-1]}'"

        if result.readline() != '':
            return f"Result had more lines than reference"
        if reference.readline() != '':
            return f"Result had fewer lines than reference"

        return None
