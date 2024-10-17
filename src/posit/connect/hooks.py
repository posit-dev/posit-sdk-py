import json
import warnings
from http.client import responses

import requests
from requests import Response

from .errors import ClientError


def handle_errors(response: Response, *args, **kwargs) -> Response:
    if response.status_code >= 400:
        try:
            data = response.json()
            error_code = data["code"]
            message = data["error"]
            payload = data.get("payload")
            http_status = response.status_code
            http_status_message = responses.get(http_status, "Unknown status")
            raise ClientError(error_code, message, http_status, http_status_message, payload)
        finally:
            response.raise_for_status()  # Raise if no JSON error is available
    return response


def check_for_deprecation_header(response: Response, *args, **kwargs) -> Response:
    """
    Check for deprecation warnings from the server.

    You might get these if you've upgraded the Connect server but not posit-sdk.
    posit-sdk will make the right request based on the version of the server,
    but if you have an old version of the package, it won't know the new URL
    to request.
    """
    if "X-Deprecated-Endpoint" in response.headers:
        msg = (
            response.url
            + " is deprecated and will be removed in a future version of Connect."
            + " Please upgrade `posit-sdk` in order to use the new APIs."
        )
        warnings.warn(msg, DeprecationWarning)
    return response
