from __future__ import annotations

import os

from typing_extensions import Any


def update_dict_values(obj: dict[str, Any], /, **kwargs: Any) -> None:
    """
    Update the values of a dictionary.

    This helper method exists as a workaround for the `dict.update` method. Sometimes, `super()` does not return the `dict` class and. If `super().update(**kwargs)` is called unintended behavior will occur.

    Therefore, this helper method exists to update the `dict`'s values.

    Parameters
    ----------
    obj : dict[str, Any]
        The object to update.
    kwargs : Any
        The key-value pairs to update the object with.

    See Also
    --------
    * https://github.com/posit-dev/posit-sdk-py/pull/366#discussion_r1887845267
    """
    # Could also be performed with:
    # for key, value in kwargs.items():
    #     obj[key] = value

    # Use the `dict` class to explicity update the object in-place
    dict.update(obj, **kwargs)


def is_workbench() -> bool:
    """Attempts to return true if called from a piece of content running on Posit Workbench.

    There is not yet a definitive way to determine if the content is running on Workbench. This method is best-effort.
    """
    return (
        "RSW_LAUNCHER" in os.environ
        or "RSTUDIO_MULTI_SESSION" in os.environ
        or "RS_SERVER_ADDRESS" in os.environ
        or "RS_SERVER_URL" in os.environ
    )


def is_connect() -> bool:
    """Returns true if called from a piece of content running on Posit Connect.

    The Connect content will always set the environment variable `RSTUDIO_PRODUCT=CONNECT`.
    """
    return os.getenv("RSTUDIO_PRODUCT") == "CONNECT"


def is_local() -> bool:
    """Returns true if called from a piece of content running locally."""
    return not is_connect() and not is_workbench()
