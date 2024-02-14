from http.client import responses
from requests import JSONDecodeError, Response

from .errors import ClientError


def handle_errors(response: Response, *args, **kwargs) -> Response:
    if response.status_code >= 400:
        try:
            data = response.json()
            error_code = data["code"]
            message = data["error"]
            http_status = response.status_code
            http_status_message = responses[http_status]
            raise ClientError(error_code, message, http_status, http_status_message)
        except JSONDecodeError:
            # No JSON error message from Connect, so just raise
            response.raise_for_status()
    return response
