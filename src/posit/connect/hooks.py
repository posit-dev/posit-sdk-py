import warnings
from http.client import responses

from requests import JSONDecodeError, Response

from .errors import ClientError


def handle_errors(
    response: Response,
    # Arguments for the hook callback signature
    *request_hook_args,  # noqa: ARG001
    **request_hook_kwargs,  # noqa: ARG001
) -> Response:
    if response.status_code >= 400:
        try:
            data = response.json()
            error_code = data["code"]
            message = data["error"]
            payload = data.get("payload")
            http_status = response.status_code
            http_status_message = responses[http_status]
            raise ClientError(error_code, message, http_status, http_status_message, payload)
        except JSONDecodeError:
            # No JSON error message from Connect, so just raise
            response.raise_for_status()
    return response


def check_for_deprecation_header(
    response: Response,
    # Extra arguments for the hook callback signature
    *args,  # noqa: ARG001
    **kwargs,  # noqa: ARG001
) -> Response:
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
        warnings.warn(msg, DeprecationWarning, stacklevel=3)
    return response
