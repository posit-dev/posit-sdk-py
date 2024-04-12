import os
import pytest

from unittest.mock import patch

from posit.connect import config


@pytest.fixture(autouse=True)
def setup():
    config.reset()
    yield


class TestSingletonBehavior:
    def test(self):
        c = config.Config()
        assert c
        assert c == config.Config()
        config.reset()
        assert c != config.Config()


class TestApiKey:
    def test(self):
        api_key = "12345"
        c = config.Config()
        c.api_key = api_key
        assert c.api_key == api_key

    def test_env(self, monkeypatch: pytest.MonkeyPatch):
        api_key = "12345"
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
        url = "http://example.com/__api__"
        c = config.Config()
        c.url = url
        assert c.url == url

    def test_env(self, monkeypatch: pytest.MonkeyPatch):
        url = "http://example.com/__api__"
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
