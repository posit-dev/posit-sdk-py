import io

import pytest

from requests import HTTPError, Response

from .errors import ClientError
from .hooks import handle_errors


def test():
    response = Response()
    response.status_code = 200
    assert handle_errors(response) == response


def test_client_error_with_plaintext_payload():
    response = Response()
    response.status_code = 404
    response.raw = io.BytesIO(b"Plain text 404 Not Found")
    with pytest.raises(HTTPError):
        handle_errors(response)


def test_client_error_with_json_payload():
    response = Response()
    response.status_code = 400
    response.raw = io.BytesIO(b'{"code":0,"error":"foobar"}')
    with pytest.raises(
        ClientError, match=r"foobar \(Error Code: 0, HTTP Status: 400 Bad Request\)"
    ):
        handle_errors(response)


def test_client_error_without_payload():
    response = Response()
    response.status_code = 404
    response.raw = io.BytesIO(b"Plain text 404 Not Found")
    with pytest.raises(HTTPError):
        handle_errors(response)
