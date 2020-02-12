from argparse import ArgumentParser, Namespace
from typing import Type, Iterator, List, Optional, Any, Union, Dict, Iterable

from ..util.dynamic_defaults import dynamic_default, with_dynamic_defaults
from ._Option import Option


class OptionHandler(object):
    """
    Super class for option-handling classes.
    """
    # The registry of option handler classes
    __registry: Dict[str, Type['OptionHandler']] = {}

    # The parser that handles the class' options
    _parser: ArgumentParser

    def __init_subclass__(cls, **kwargs):
        # Add the new sub-class to the registry
        OptionHandler.__registry[f"{cls.__module__}.{cls.__name__}"] = cls

        # Initialise the sub-class' parser
        cls._initialise_parser()

        return super().__init_subclass__(**kwargs)

    @classmethod
    def _initialise_parser(cls):
        """
        Initialises the parser for this class.
        """
        # Create the class argument parser
        cls._parser = ArgumentParser(description=f"{cls.__module__}.{cls.__name__}")

        # Add any class options to the parser
        for option in cls._get_all_options():
            option.configure_parser(cls._parser)

    @classmethod
    def _get_all_options(cls) -> Iterator[Option]:
        """
        Gets all options for this option handler.

        :return:    An iterator over the options.
        """
        for name in dir(cls):
            # Option names can't start with underscores
            if name.startswith("_"):
                continue

            # Get the attribute
            obj = getattr(cls, name)

            # If it's an option descriptor, yield it
            if isinstance(obj, Option):
                yield obj

    @classmethod
    def get_all_options(cls) -> Iterator[str]:
        """
        Gets the names of all options on this class.

        :return:    An iterator of option names.
        """
        return (option.name for option in cls._get_all_options())

    @classmethod
    def get_common_options(cls, other: Type['OptionHandler']) -> Iterator[str]:
        """
        Gets the options common to this handler and another.

        :param other:   The other option handler.
        :return:        The set of common option names.
        """
        # Get the other's options, keyed by name
        other_options = {option.name: option for option in other._get_all_options()}

        # Return all option names which refer to identical options
        return (option.name
                for option in cls._get_all_options()
                if option.name in other_options
                and other_options[option.name] == option)

    @with_dynamic_defaults
    def __init__(self, options=dynamic_default(list)):
        """
        Initializes the reader.

        :param options: the options to use
        :type options: list
        """
        self._namespace: Namespace = Namespace()
        self._options_list: List[str] = []

        # now initialize options/namespace
        self.options = options

    def get_option_value(self, option: Union[str, Option]) -> Any:
        """
        Gets the current value for an option.

        :param option:  The option, by name or reference.
        :return:        The option's value.
        """
        # Convert options to their name
        if isinstance(option, Option):
            option = option.name

        # Get the value from the namespace by name
        return getattr(self._namespace, option)

    def get_options_sub_list(self, options: Iterable[Union[str, Option]]) -> List[str]:
        """
        Gets the part of the options list which corresponds to
        the given option.

        :param options: The options, by name or reference.
        :return:        The option's option-list segments.
        """
        # Get the set of option names
        option_names = set(option if isinstance(option, str) else option.name
                           for option in options)

        # Convert option names to option references
        options = list(getattr(type(self), option) for option in option_names)

        # Convert references to option strings
        option_strings = set(option.option_string for option in options)

        # Get the slices of the options list corresponding to the option
        options_sub_list = []
        slice_started: bool = False
        for string in self._options_list:
            # See if we are in a valid slice
            if string.startswith("--"):
                slice_started = string in option_strings

            # Add the string to the sub-list if it's part of a valid slice
            if slice_started:
                options_sub_list.append(string)

        return options_sub_list

    @property
    def options(self):
        """
        Returns the currently used options.

        :return: the list of options (strings)
        :rtype: list
        """
        return self._options_list.copy()

    @options.setter
    def options(self, options: Optional[List[str]]):
        """
        Sets the options to use.

        :param options: the list of options, can be None
        """
        # Copy the options list
        self._options_list = [] if options is None else options.copy()

        # Parse the options
        self._namespace = self._parser.parse_args(options)

    @classmethod
    def options_help(cls) -> str:
        """
        Returns the help for the options.

        :return: the help
        """
        return cls._parser.format_help()
