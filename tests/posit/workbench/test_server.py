"""Tests for the shared Server resource manager."""

import responses

from posit.workbench.server import Server
from posit.workbench.urls import Url

SERVER_URL = "https://workbench.example.com"


class _FakeClient:
    """Minimal stand-in exposing just what the shared resource managers need."""

    def __init__(self, server_url: str = SERVER_URL):
        import requests

        self.server_url = Url(server_url)
        self.session = requests.Session()

    def post(self, path, **kwargs):
        """Post to the fake server, joining the base URL and path."""
        return self.session.post(f"{self.server_url}/{path}", **kwargs)


class _FakeContext:
    """Minimal stand-in for either concrete client's Context."""

    def __init__(self, client=None):
        self.client = client or _FakeClient()


def _api_url(method: str) -> str:
    return f"{SERVER_URL}/api/{method}"


class TestVersion:
    """Tests for Server.version()."""

    @responses.activate
    def test_version_returns_bare_envelope(self):
        """Regression test: version returns its payload bare, not wrapped in `{"result": ...}`.

        Confirmed against a live server: unlike every other method, this is the one case
        where call_raw() (not call()) must be used.
        """
        responses.add(
            responses.POST,
            _api_url("version"),
            json={"version": {"major": "2025", "minor": "12"}, "features": ["jobs"]},
            status=200,
        )
        info = Server(_FakeContext()).version()
        assert info["features"] == ["jobs"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        assert info["version"] == {"major": "2025", "minor": "12"}  # pyright: ignore[reportTypedDictNotRequiredAccess]
