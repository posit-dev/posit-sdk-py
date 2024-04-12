import pytest

from unittest.mock import patch

from posit.connect import config


@patch.dict("os.environ", {"CONNECT_API_KEY": "foobar"})
def test_get_api_key():
    api_key = config._get_api_key()
    assert api_key == "foobar"


@patch.dict("os.environ", {"CONNECT_API_KEY": ""})
def test_get_api_key_empty():
    with pytest.raises(ValueError):
        config._get_api_key()


@patch.dict("os.environ", clear=True)
def test_get_api_key_miss():
    with pytest.raises(ValueError):
        config._get_api_key()


@patch.dict("os.environ", {"CONNECT_SERVER": "http://foo.bar"})
def test_get_url():
    url = config._get_url()
    assert url == "http://foo.bar"


@patch.dict("os.environ", {"CONNECT_SERVER": ""})
def test_get_url_empty():
    with pytest.raises(ValueError):
        config._get_url()


@patch.dict("os.environ", clear=True)
def test_get_url_miss():
    with pytest.raises(ValueError):
        config._get_url()


def test_init():
    api_key = "foobar"
    url = "http://foo.bar/__api__"
    c = config.Config(api_key=api_key, url=url)
    assert c.api_key == api_key
    assert c.url == url
