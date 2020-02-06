from argparse import Action, FileType, ArgumentParser
from typing import Optional, Type, Union, Any, Iterable, Callable, Tuple, TypeVar, Dict

from ..util import non_default_kwargs

# The type of the option's value
T = TypeVar("T")


class Option:
    """
    Descriptor class which sets an option on an option-handler.
    """
    def __init__(self, *,
                 action: Union[str, Type[Action]] = ...,
                 nargs: Union[int, str] = ...,
                 const: Any = ...,
                 default: Any = ...,
                 type: Union[Callable[[str], T], FileType] = ...,
                 choices: Iterable[T] = ...,
                 required: bool = ...,
                 help: Optional[str] = ...,
                 metavar: Union[str, Tuple[str, ...]] = ...
                 ):
        self._name: str = ""

        # Save any non-default arguments as kwargs
        self._kwargs: Dict[str, Any] = non_default_kwargs(Option.__init__, locals())

    @property
    def name(self) -> str:
        """
        Gets the name of this option.

        :return: The option's name.
        """
        return self._name

    @property
    def option_string(self) -> str:
        """
        Gets the option name-string for this option.

        :return:    The option string.
        """
        return f"--{self._name.replace('_', '-')}"

    def __get__(self, instance: Optional['OptionHandler'], owner: Type['OptionHandler']):
        # If called on the class, return the option itself
        if instance is None:
            return self

        # Get the value from the option handler's parsed options
        return instance.get_option_value(self)

    def __set_name__(self, owner: 'Type[OptionHandler]', name: str):
        # Only optional handlers can use options
        from ._OptionHandler import OptionHandler
        if not issubclass(owner, OptionHandler):
            raise TypeError(f"Class {owner.__name__} is not an OptionHandler")

        # Can't have private options
        if name.startswith("_"):
            raise ValueError(f"Option names can't start with underscores")

        # If we already have a name, setting this option against
        # another owner requires that it use the same name
        if self._name != "" and name != self._name:
            raise NameError(f"Attempted to rename option '{self._name}' to '{name}'. "
                            f"If reusing an option, the name must remain the same")

        self._name = name

    def configure_parser(self, parser: ArgumentParser):
        """
        Configures a parser to handle this option.

        :param parser:  The parser to configure.
        """
        parser.add_argument(self.option_string,
                            dest=self._name,
                            **self._kwargs)

    def __eq__(self, other) -> bool:
        # Must be an option
        if not isinstance(other, Option):
            return False

        return self is other or self._kwargs == other._kwargs
