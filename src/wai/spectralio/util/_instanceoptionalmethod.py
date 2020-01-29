from functools import wraps
from inspect import isclass


class instanceoptionalmethod:
    """
    Decorator class (like classmethod/staticmethod) which provides
    the class as the first implicit parameter, and the instance as
    the second (if called on an instance) or None (if not).

    Copied from wai.common.
    """
    def __init__(self, function):
        self._function = function

    def __get__(self, instance, owner):
        @wraps(self._function)
        def intern(*args, **kwargs):
            return self._function(instance if instance is not None else owner, *args, **kwargs)

        return intern

    @staticmethod
    def is_instance(self) -> bool:
        """
        Checks if the given reference is an instance or a class.

        :param self:    The instance/class reference.
        :return:        True if the reference is an instance,
                        False if it is a class.
        """
        return not isclass(self)
