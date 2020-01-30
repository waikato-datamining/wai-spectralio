from functools import wraps
from inspect import isclass
from typing import Type, TypeVar, Union

# Type variable for the instance type
T = TypeVar("T")


class instanceoptionalmethod:
    """
    Decorator class (like classmethod/staticmethod) which provides
    the class as the first implicit parameter, and the instance as
    the second (if called on an instance) or None (if not).
    """
    def __init__(self, function):
        self._function = function

    def __get__(self, instance, owner):
        @wraps(self._function)
        def intern(*args, **kwargs):
            return self._function(instance if instance is not None else owner, *args, **kwargs)

        return intern

    @staticmethod
    def is_instance(self: Union[T, Type[T]]) -> bool:
        """
        Checks if the given reference is an instance or a class.

        :param self:    The instance/class reference.
        :return:        True if the reference is an instance,
                        False if it is a class.
        """
        return not isclass(self)

    @staticmethod
    def type(self: Union[T, Type[T]]) -> Type[T]:
        """
        Helper method which gets the class from self.

        :param self:    The instance/class reference.
        :return:        The class.
        """
        if instanceoptionalmethod.is_instance(self):
            return type(self)

        return self
