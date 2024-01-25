from http.client import responses
from requests import Response

from .errors import ClientError


def handle_errors(response: Response, *args, **kwargs) -> Response:
    if response.status_code >= 400 and response.status_code < 500:
        data = response.json()
        error_code = data["code"]
        message = data["error"]
        http_status = response.status_code
        http_status_message = responses[http_status]
        raise ClientError(error_code, message, http_status, http_status_message)
    return response
