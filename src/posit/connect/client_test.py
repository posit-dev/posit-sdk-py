import pytest

from unittest.mock import MagicMock, patch

from .client import Client, _get_api_key, _get_endpoint


class TestClient:
    @patch("posit.connect.client.Users")
    @patch("posit.connect.client.Session")
    @patch("posit.connect.client.Auth")
    def test_init(self, Auth: MagicMock, Session: MagicMock, Users: MagicMock):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        client = Client(api_key=api_key, endpoint=endpoint)
        assert client._api_key == api_key
        assert client._endpoint == endpoint
        Session.assert_called_once()
        Auth.assert_called_once_with(api_key)
        Users.assert_called_once_with(endpoint, Session.return_value)


class TestGetApiKey:
    @patch.dict("os.environ", {"CONNECT_API_KEY": "foobar"})
    def test_get_api_key(self):
        api_key = _get_api_key()
        assert api_key == "foobar"

    @patch.dict("os.environ", {"CONNECT_API_KEY": ""})
    def test_get_api_key_empty(self):
        with pytest.raises(ValueError):
            _get_api_key()

    def test_get_api_key_miss(self):
        with pytest.raises(ValueError):
            _get_api_key()


class TestGetEndpoint:
    @patch.dict("os.environ", {"CONNECT_SERVER": "http://foo.bar"})
    def test_get_endpoint(self):
        endpoint = _get_endpoint()
        assert endpoint == "http://foo.bar"

    @patch.dict("os.environ", {"CONNECT_SERVER": ""})
    def test_get_endpoint_empty(self):
        with pytest.raises(ValueError):
            _get_endpoint()

    def test_get_endpoint_miss(self):
        with pytest.raises(ValueError):
            _get_endpoint()
