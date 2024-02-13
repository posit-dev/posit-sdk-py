import pytest

from unittest.mock import patch

from .config import Config, _get_api_key, _get_endpoint


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


class TestConfig:
    def test_init(self):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        config = Config(api_key=api_key, endpoint=endpoint)
        assert config.api_key == api_key
        assert config.endpoint == endpoint
