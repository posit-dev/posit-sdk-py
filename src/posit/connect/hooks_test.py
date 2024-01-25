import pytest

from unittest.mock import Mock

from .hooks import handle_errors


class TestHandleErrors:
    def test(self):
        response = Mock()
        response.status_code = 200
        assert handle_errors(response) == response

    def test_client_error(self):
        response = Mock()
        response.status_code = 400
        response.json = Mock()
        response.json.return_value = {"code": 0, "error": "foobar"}
        with pytest.raises(Exception):
            handle_errors(response)
