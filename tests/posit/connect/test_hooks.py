import io
from unittest.mock import Mock

import pytest
import responses
from requests import HTTPError, JSONDecodeError, Response

from posit.connect import Client
from posit.connect.errors import ClientError
from posit.connect.hooks import handle_errors


def test_success():
    response = Mock()
    response.status_code = 200
    assert handle_errors(response) == response


def test_client_error():
    response = Mock()
    response.status_code = 400
    response.json = Mock(return_value={"code": 0, "error": "foobar"})
    with pytest.raises(ClientError):
        handle_errors(response)


def test_client_error_without_payload():
    class StatusException(Exception):
        pass

    response = Mock()
    response.status_code = 404
    response.json = Mock(side_effect=JSONDecodeError("Test code", "Test msg", 0))
    response.raise_for_status = Mock(side_effect=StatusException())
    with pytest.raises(StatusException):
        handle_errors(response)


def test_200():
    response = Response()
    response.status_code = 200
    assert handle_errors(response) == response


def test_response_client_error_with_plaintext_payload():
    response = Response()
    response.status_code = 404
    response.raw = io.BytesIO(b"Plain text 404 Not Found")
    with pytest.raises(HTTPError):
        handle_errors(response)


def test_response_client_error_with_json_payload():
    response = Response()
    response.status_code = 400
    response.raw = io.BytesIO(b'{"code":0,"error":"foobar"}')
    with pytest.raises(
        ClientError,
        match='{"error_code": 0, "error_message": "foobar", "http_status": 400, "http_message": "Bad Request", "payload": null}',
    ):
        handle_errors(response)


def test_response_client_error_without_payload():
    response = Response()
    response.status_code = 404
    response.raw = io.BytesIO(b"Plain text 404 Not Found")
    with pytest.raises(HTTPError):
        handle_errors(response)


@responses.activate
def test_deprecation_warning():
    responses.get(
        "https://connect.example/__api__/v0",
        headers={"X-Deprecated-Endpoint": "v1/"},
    )
    c = Client("https://connect.example", "12345")

    with pytest.warns(DeprecationWarning):
        c.get("v0")
