from typing import Optional, TypeVar, Callable

from .constants import BLOCK_TYPE_SPEC_MASK

GetType = TypeVar("GetType")


class Block:
    """
    Convenience class for handling blocks.
    """
    def __init__(self,
                 buffer: bytes,
                 definition: int,
                 start: int,
                 end: int,
                 type_: int):
        self.buffer: bytes = buffer
        self.definition: int = definition
        self.start: int = start
        self.end: int = end if end < len(buffer) else len(buffer) - 1
        self.type: int = type_
        self.name: Optional[str] = None

        try:
            if len(buffer) > 3:
                name = buffer[start:start + 3].decode("ascii")
                if name.isalpha():
                    self.name = name
        except UnicodeDecodeError:
            pass

    def __len__(self):
        """
        Returns the size of the block.

        :return:    The size.
        """
        return self.end - self.start + 1

    def has_id(self, id_: bytes) -> bool:
        """
        Whether the ID is present in the block.

        :param id_:     The ID to check.
        :return:        True if present.
        """
        return self.find_id(id_) is not None

    def get(self, offset: int, get_func: Callable[[bytes, int], GetType]) -> GetType:
        """
        Gets something from the given offset in the buffer.

        :param offset:      The offset to get from.
        :param get_func:    The func to get with.
        :return:            The something.
        """
        return get_func(self.buffer, self.start + offset)

    def get_from_id(self,
                    id_: bytes,
                    offset: int,
                    get_func: Callable[[bytes, int], GetType]) -> Optional[GetType]:
        """
        Gets something from the buffer at a given offset from the ID.

        :param id_:         The ID to offset from.
        :param offset:      The offset.
        :param get_func:    The function to use to get something.
        :return:            The thing, or None if the ID isn't found.
        """
        pos: Optional[int] = self.find_id(id_)

        if pos is None:
            return None

        return self.get(pos + offset, get_func)

    def find_id(self, id_: bytes) -> Optional[int]:
        """
        Locates the position of the given ID in the buffer.

        :param id_:     The ID to find.
        :return:        The position, or None if not found.
        """
        for pos in range(self.start, self.end + 1 - len(id_)):
            if self.buffer[pos:pos + len(id_)] == id_:
                return pos - self.start

        return None

    def get_buffer(self) -> bytes:
        """
        Gets a copy of the buffer.

        :return:    The buffer copy.
        """
        return bytes(self.buffer[self.start:self.end + 1])

    def __str__(self):
        masked_type_hex = (self.type & BLOCK_TYPE_SPEC_MASK).to_bytes(3, "big", signed=False).hex()[-5:]
        return (
            f"definition={self.definition}, "
            f"type={self.type}, "
            f"maskedTypeHex={masked_type_hex}, "
            f"name={self.name}, "
            f"start={self.start}, "
            f"end={self.end}"
        )
