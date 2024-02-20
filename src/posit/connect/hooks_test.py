import pytest

from unittest.mock import Mock, patch

from .errors import ClientError
from .hooks import handle_errors


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
