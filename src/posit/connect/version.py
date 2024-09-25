from functools import wraps

from packaging.version import Version

from .exceptions import VersionUpgradeRequiredException


def requires_version(expected: str):
    """
    Decorator to enforce a minimum version requirement for a method.

    This decorator checks the `version` attribute of the class instance and raises a `VersionUpgradeRequiredException` if the version is lower than the specified `expected` version.

    Parameters
    ----------
    expected : str
        The minimum version required for the decorated method to execute. It is compared against the class instance's `version` attribute.

    Returns
    -------
    function
        The wrapped function that enforces the version check.

    Raises
    ------
    VersionUpgradeRequiredException
        If the version specified in the class instance's `version` attribute is lower than the `expected` version.

    Examples
    --------
    To use this decorator, apply it to any method that requires a minimum version:

    >>> class Client:
    >>>     version = "2024.07.0"
    >>>
    >>>     @requires_version("2024.08.0")
    >>>     def some_method(self):
    >>>         pass
    >>>
    >>> client = Client()
    >>> client.some_method()
    Traceback (most recent call last):
    ...
    VersionUpgradeRequiredException: This API is not available in Connect version 2024.07.0. Please upgrade to version 2024.08.0 or later."

    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, "version"):
                version = getattr(self, "version")
                if version and Version(version) < Version(expected):
                    raise VersionUpgradeRequiredException(version, expected)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
