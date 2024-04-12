import os
import pytest

from unittest.mock import patch

from posit.connect import config


@pytest.fixture(autouse=True)
def setup():
    # capture the convert config settings
    c = config.Config()
    # reset the config before each test
    config.Config.instance = None
    # invoke the test
    yield
    # set the config back to previous state
    config.Config.instance = c


class TestApiKey:
    def test(self):
        c = config.Config()
        api_key = "test-api-key"
        c.api_key = api_key
        assert c.api_key == api_key

    def test_env(self, monkeypatch: pytest.MonkeyPatch):
        api_key = "test-api-key"
        monkeypatch.setenv("CONNECT_API_KEY", api_key)
        assert os.getenv("CONNECT_API_KEY") == api_key
        c = config.Config()
        c.api_key == api_key

    def test_env_missing(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("CONNECT_API_KEY", raising=False)
        assert os.getenv("CONNECT_API_KEY") is None
        c = config.Config()
        with pytest.raises(ValueError):
            c.api_key


class TestUrl:
    def test(self):
        url = f"http://test-url.com/__api__"
        c = config.Config()
        c.url = url
        assert c.url == url

    def test_env(self, monkeypatch: pytest.MonkeyPatch):
        url = f"http://test-url.com/__api__"
        monkeypatch.setenv("CONNECT_SERVER", url)
        assert os.getenv("CONNECT_SERVER") == url
        c = config.Config()
        c.url == url

    def test_env_missing(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("CONNECT_SERVER", raising=False)
        assert os.getenv("CONNECT_SERVER") is None
        c = config.Config()
        with pytest.raises(ValueError):
            c.url
