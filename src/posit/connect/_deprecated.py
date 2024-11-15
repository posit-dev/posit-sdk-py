import warnings


# From https://github.com/posit-dev/py-shiny/blob/f6b92d8cf49a90f3b3dbb636cd6d7fdeee244cfd/shiny/_deprecated.py#L15C1-L28C1
# Create our own warning class instead of using built-in DeprecationWarning, because we
# want to be able to control display of these messages without interfering with the
# user's control of DeprecationWarning.
# 2024-11: Change base class to DeprecationWarning
class PositConnectDeprecationWarning(DeprecationWarning):
    pass


# By default DeprecationWarnings aren't shown; we want to always show them.
warnings.simplefilter("always", PositConnectDeprecationWarning)


def warn_deprecated(message: str, stacklevel: int = 3):
    warnings.warn(message, PositConnectDeprecationWarning, stacklevel=stacklevel)


def warn_deprecated_and_removed_in_future(message: str, stacklevel: int = 3):
    message += " This method will be removed in a future release."
    warnings.warn(message, PositConnectDeprecationWarning, stacklevel=stacklevel)
