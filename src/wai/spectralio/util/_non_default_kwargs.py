from inspect import Signature, signature, Parameter
from typing import Any, Dict


def non_default_kwargs(function, locals_) -> Dict[str, Any]:
    """
    Gets a dictionary of all keyword-only arguments which
    have non-default values.

    E.g.
    def my_func(*, kw1=None, kw2=None, kw3=None):
        return non_default_kwargs(my_func, locals())

    nd_kwargs = my_func(kw1=1, kw3=3)

    assert nd_kwargs == {"kw1": 1, "kw3": 3}

    :param function:    The function being called.
    :param locals_:     The locals in the function.
    :return:            The mapping from keyword to value for
                        all non-default keyword arguments.
    """
    # Get the function signature
    function_signature: Signature = signature(function)

    return {name: locals_[name]
            for name, parameter in function_signature.parameters.items()
            if parameter.kind == Parameter.KEYWORD_ONLY
            and locals_[name] is not parameter.default}
