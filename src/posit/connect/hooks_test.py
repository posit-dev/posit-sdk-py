import pytest

from requests import HTTPError, JSONDecodeError
from unittest.mock import Mock

from .errors import ClientError
from .hooks import handle_errors


class TestHandleErrors:
    def test(self):
        response = Mock()
        response.status_code = 200
        assert handle_errors(response) == response

    def test_client_error(self):
        response = Mock()
        response.status_code = 400
        response.json = Mock(return_value={"code": 0, "error": "foobar"})
        with pytest.raises(ClientError):
            handle_errors(response)

    def test_client_error_not_json(self):
        response = Mock()
        response.status_code = 404
        response.json = Mock(side_effect=JSONDecodeError("Not Found", "", 0))
        response.raise_for_status = Mock(side_effect=HTTPError())
        with pytest.raises(HTTPError):
            handle_errors(response)
