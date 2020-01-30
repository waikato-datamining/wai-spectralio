import functools
import locale


def with_locale(locale_to_use: str, category: int = locale.LC_NUMERIC):
    """
    Function which creates a decorator which sets the locale before
    the wrapped function is called, and reverts it after it is finished.

    :param locale_to_use:   The locale to use.
    :param category:        The locale category to modify.
    :return:                The decorator.
    """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            # Save the current locale
            saved_locale = locale.getlocale(category)

            # Set the locale
            try:
                locale.setlocale(category, (locale_to_use, "UTF-8"))
            except locale.Error as e:
                e.args = *e.args, locale_to_use
                raise

            try:
                return function(*args, **kwargs)
            finally:
                locale.setlocale(category, saved_locale)

        return wrapper

    return decorator
