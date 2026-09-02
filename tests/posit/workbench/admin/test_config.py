"""Tests for the Bearer-token client's configuration resolution."""

import pytest

from posit.workbench.admin.config import Config


class TestConfigResolution:
    """Tests for resolving the server URL and API token from args/env vars."""

    def test_explicit_args_take_precedence(self, monkeypatch):
        """Explicit url/api_key arguments win over environment variables."""
        monkeypatch.setenv("WORKBENCH_SERVER", "https://env.example.com")
        monkeypatch.setenv("WORKBENCH_API_KEY", "env-key")
        cfg = Config(url="https://explicit.example.com", api_key="explicit-key")
        assert cfg.url == "https://explicit.example.com"
        assert cfg.api_key == "explicit-key"

    def test_falls_back_to_env_vars(self, monkeypatch):
        """With no explicit args, WORKBENCH_SERVER/WORKBENCH_API_KEY are used."""
        monkeypatch.setenv("WORKBENCH_SERVER", "https://env.example.com")
        monkeypatch.setenv("WORKBENCH_API_KEY", "env-key")
        cfg = Config()
        assert cfg.url == "https://env.example.com"
        assert cfg.api_key == "env-key"

    def test_raises_without_url(self, monkeypatch):
        """Missing WORKBENCH_SERVER (and no explicit url) raises ValueError."""
        monkeypatch.delenv("WORKBENCH_SERVER", raising=False)
        monkeypatch.setenv("WORKBENCH_API_KEY", "env-key")
        with pytest.raises(ValueError, match="WORKBENCH_SERVER"):
            Config()

    def test_raises_without_api_key(self, monkeypatch):
        """Missing WORKBENCH_API_KEY (and no explicit api_key) raises ValueError."""
        monkeypatch.setenv("WORKBENCH_SERVER", "https://env.example.com")
        monkeypatch.delenv("WORKBENCH_API_KEY", raising=False)
        with pytest.raises(ValueError, match="WORKBENCH_API_KEY"):
            Config(url="https://env.example.com")
