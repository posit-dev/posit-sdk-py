import os

"""
NOTE: The APIs in this module are provided as a convenience and are subject to breaking changes.
"""

def _is_local() -> bool:
    """Returns true if called from a piece of content running on a Connect server.

    The connect server will always set the environment variable `RSTUDIO_PRODUCT=CONNECT`.
    We can use this environment variable to determine if the content is running locally
    or on a Connect server.
    """
    return not os.getenv("RSTUDIO_PRODUCT") == "CONNECT"
