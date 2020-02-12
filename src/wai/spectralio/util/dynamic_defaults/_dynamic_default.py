from typing import TypeVar, Callable

# The type of the dynamic default values
DefaultType = TypeVar("DefaultType")


class _DynamicDefault:
    """
    Class which determines that the default value for a
    function should be recalculated per-call.
    """
    def __init__(self, default: Callable[[], DefaultType]):
        self._default: Callable[[], DefaultType] = default

    def get(self) -> DefaultType:
        return self._default()


dynamic_default = _DynamicDefault
