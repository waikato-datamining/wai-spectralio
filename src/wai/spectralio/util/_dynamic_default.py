import functools
from inspect import signature, Signature, Parameter, BoundArguments
from typing import Any, Callable, Optional


def dynamic_default(default_func: Callable[[], Any],
                    name: str):
    """
    Function which creates a decorator that provides a default
    value to a parameter if it is given the value None.

    :param default_func:    The function to call to generate the default value.
    :param keyword:         The argument's name.
    :return:                The decorator function.
    """
    def decorator(function):
        # Make sure the function has a parameter with the given name
        function_signature: Signature = signature(function)
        if name not in function_signature.parameters:
            raise ValueError(f"Decorated function '{function.__name__}' has no parameter '{name}'")

        # Get the parameter reference
        parameter: Parameter = function_signature.parameters[name]

        # Make sure the parameter's default is None
        if parameter.default is not None:
            raise ValueError(f"Parameter '{name}' is not suitable for dynamic defaults "
                             f"as its static default is not None")

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            # Attempt to resolve the binding of parameters
            try:
                binding: BoundArguments = function_signature.bind(*args, **kwargs)
                binding.apply_defaults()

                # Modify the parameter if it is defaulted
                if binding.arguments[parameter.name] is None:
                    binding.arguments[parameter.name] = default_func()

                args = binding.args
                kwargs = binding.kwargs

            except TypeError:
                # Ignore the error as it will be raised again when the
                # function itself is called
                pass

            return function(*args, **kwargs)

        return wrapper

    return decorator
