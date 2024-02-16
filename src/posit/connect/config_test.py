import pytest

from unittest.mock import MagicMock, patch

from .config import Config, _get_api_key, _get_url


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


class TestGetUrl:
    @patch.dict("os.environ", {"CONNECT_SERVER": "http://foo.bar"})
    def test_get_endpoint(self):
        url = _get_url()
        assert url == "http://foo.bar"

    @patch.dict("os.environ", {"CONNECT_SERVER": ""})
    def test_get_endpoint_empty(self):
        with pytest.raises(ValueError):
            _get_url()

    def test_get_endpoint_miss(self):
        with pytest.raises(ValueError):
            _get_url()


class TestConfig:
    @patch("posit.connect.config.Url")
    def test_init(self, Url: MagicMock):
        api_key = "foobar"
        url = "http://foo.bar"
        config = Config(api_key=api_key, url=url)
        assert config.api_key == api_key
        assert config.url == Url.return_value
        Url.assert_called_with(url)
