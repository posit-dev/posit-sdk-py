from __future__ import annotations

import os


def get_product() -> str | None:
    """Returns the product name if called with a Posit product.

    The products will always set the environment variable `POSIT_PRODUCT=<product-name>`
    or `RSTUDIO_PRODUCT=<product-name>`.

    RSTUDIO_PRODUCT is deprecated and acts as a fallback for backwards compatibility.
    It is recommended to use POSIT_PRODUCT instead.
    """
    return os.getenv("POSIT_PRODUCT") or os.getenv("RSTUDIO_PRODUCT")


def is_local() -> bool:
    """Returns true if called while running locally."""
    return get_product() is None


def is_running_on_connect() -> bool:
    """Returns true if called from a piece of content running on a Connect server."""
    return get_product() == "CONNECT"


def is_running_on_workbench() -> bool:
    """Returns true if called from within a Workbench server."""
    return get_product() == "WORKBENCH"
