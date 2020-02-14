from functools import wraps

from ._SerialisationError import SerialisationError


def ensure_errors(function):
    """
    Decorator which makes sure that any exceptions raised
    by the function are of the SerialisationError type or
    a sub-type.

    :param function:    The function to decorate.
    :return:            The decorated function.
    """
    @wraps(function)
    def with_errors_ensured(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except SerialisationError:
            raise
        except Exception as e:
            raise SerialisationError(f"Unhandled serialisation error: {e}") from e

    return with_errors_ensured
