import io

import pytest
import responses

from requests import HTTPError, Response
from unittest.mock import Mock, patch

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


@patch("posit.connect.hooks.JSONDecodeError")
def test_client_error_without_payload(JSONDecodeError):
    response = Mock()
    response.status_code = 404
    response.json = Mock(side_effect=JSONDecodeError())
    response.raise_for_status = Mock(side_effect=Exception())
    with pytest.raises(Exception):
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
        match=r"foobar \(Error Code: 0, HTTP Status: 400 Bad Request\)",
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
    c = Client("12345", "https://connect.example")

    with pytest.warns(DeprecationWarning):
        c.get("v0")
