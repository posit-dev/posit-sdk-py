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


def is_local() -> bool:
    """Returns true if called from a piece of content running on a Connect server.

    The connect server will always set the environment variable `RSTUDIO_PRODUCT=CONNECT`.
    We can use this environment variable to determine if the content is running locally
    or on a Connect server.
    """
    return os.getenv("RSTUDIO_PRODUCT") != "CONNECT"
