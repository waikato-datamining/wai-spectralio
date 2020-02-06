import os
from abc import abstractmethod
from io import BytesIO
from typing import Generic, TypeVar, IO

# The type of object the serialiser serialises/deserialises
ObjectType = TypeVar("ObjectType")


class Serialiser(Generic[ObjectType]):
    """
    Base class for objects which serialise other objects
    to/from a binary representation.
    """
    # ============= #
    # Serialisation #
    # ============= #
    @abstractmethod
    def _check(self, obj: ObjectType):
        """
        Checks the object is suitable for serialisation.

        :param obj:             The object to check.
        :raises Exception:      If the object is not suitable for serialisation.
        """
        pass

    @abstractmethod
    def _serialise(self, obj: ObjectType, stream: IO[bytes]):
        """
        Serialises the given object to the given data-stream.

        :param obj:         The object to serialise.
        :param stream:      The stream to write the object to.
        """
        pass

    def serialise(self, obj: ObjectType, stream: IO[bytes]):
        """
        Serialises the given object to the given data-stream.

        :param obj:         The object to serialise.
        :param stream:      The stream to write the object to.
        """
        self._check(obj)
        self._serialise(obj, stream)

    def serialise_to_file(self, obj: ObjectType, filename: str):
        """
        Serialises the object to a file.

        :param obj:         The object to serialise.
        :param filename:    The name of the file to serialise to.
        """
        # Make sure the directory for the file exists
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        # Save the file
        with open(filename, 'wb') as file:
            self.serialise(obj, file)

    def serialise_to_bytes(self, obj: ObjectType) -> bytes:
        """
        Gets the serialised state of the object.

        :param obj:     The object to serialise.
        """
        # Create an in-memory stream
        stream = BytesIO()

        # Serialise the object to the stream
        self.serialise(obj, stream)

        # Reset the stream
        stream.seek(0)

        # Return the stream contents
        return stream.read()

    # =============== #
    # Deserialisation #
    # =============== #

    @abstractmethod
    def _deserialise(self, stream: IO[bytes]) -> ObjectType:
        """
        Deserialises an object from the given data-stream.

        :param stream:  The stream to read the object from.
        :return:        The deserialised object.
        """
        pass

    def deserialise(self, stream: IO[bytes]) -> ObjectType:
        """
        Deserialises an object from the given data-stream.

        :param stream:  The stream to read the object from.
        :return:        The deserialised object.
        """
        return self._deserialise(stream)

    def deserialise_from_file(self, filename: str) -> ObjectType:
        """
        Deserialises an object from the given file.

        :param filename:    The filename.
        :return:            The deserialised object.
        """
        with open(filename, 'rb') as file:
            return self.deserialise(file)

    def deserialise_from_bytes(self, data: bytes) -> ObjectType:
        """
        Deserialises an object from its serialised state.

        :param data:    The serialised object.
        :return:        The deserialised object.
        """
        return self.deserialise(BytesIO(data))
