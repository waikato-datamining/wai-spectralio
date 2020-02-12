"""
Package for adding dynamic defaults to functions. Dynamic defaults
are default values for parameters which return a new object on every call,
rather than reusing the same object each call ("static" default).

Usage:
@with_dynamic_defaults
def my_func(a=dynamic_default(MyClass)):
    ...
"""
from ._dynamic_default import dynamic_default
from ._with_dynamic_defaults import with_dynamic_defaults
