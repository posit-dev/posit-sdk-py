from unittest.mock import patch

import pytest

from posit.connect.config import Config, _get_api_key, _get_url


@patch.dict("os.environ", {"CONNECT_API_KEY": "foobar"})
def test_get_api_key():
    api_key = _get_api_key()
    assert api_key == "foobar"


@patch.dict("os.environ", {"CONNECT_API_KEY": ""})
def test_get_api_key_empty():
    with pytest.raises(ValueError):
        _get_api_key()


@patch.dict("os.environ", clear=True)
def test_get_api_key_miss():
    with pytest.raises(ValueError):
        _get_api_key()


@patch.dict("os.environ", {"CONNECT_SERVER": "http://foo.bar"})
def test_get_url():
    url = _get_url()
    assert url == "http://foo.bar"


@patch.dict("os.environ", {"CONNECT_SERVER": ""})
def test_get_url_empty():
    with pytest.raises(ValueError):
        _get_url()


@patch.dict("os.environ", clear=True)
def test_get_url_miss():
    with pytest.raises(ValueError):
        _get_url()


def test_init():
    api_key = "foobar"
    url = "http://foo.bar/__api__"
    config = Config(api_key=api_key, url=url)
    assert config.api_key == api_key
    assert config.url == url
