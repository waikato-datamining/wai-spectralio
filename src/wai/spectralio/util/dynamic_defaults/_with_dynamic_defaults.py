import functools
from inspect import Signature, signature, BoundArguments
from typing import TypeVar, Callable, Any

from ._dynamic_default import dynamic_default

# The return type of the wrapped function
ReturnType = TypeVar("ReturnType")


def with_dynamic_defaults(function: Callable[[Any], ReturnType]):
    """
    Decorator which processes dynamic defaults for the wrapped function.

    :param function:    The wrapped function with dynamic defaults.
    :return:            The decorated function.
    """
    # Get the signature of the wrapped function
    function_signature: Signature = signature(function)

    @functools.wraps(function)
    def resolve_dynamic_defaults(*args, **kwargs):
        # Bind the arguments
        binding: BoundArguments = function_signature.bind(*args, **kwargs)
        binding.apply_defaults()

        # Resolve any dynamic defaults
        for name in function_signature.parameters:
            if isinstance(binding.arguments[name], dynamic_default):
                binding.arguments[name] = binding.arguments[name].get()

        # Call the function with the resolved arguments
        return function(*binding.args, **binding.kwargs)

    return resolve_dynamic_defaults
