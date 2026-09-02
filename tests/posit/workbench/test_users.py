"""Tests for the shared Users resource manager."""

import responses

from posit.workbench.urls import Url
from posit.workbench.users import Users

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


class TestList:
    """Tests for Users.list()."""

    @responses.activate
    def test_list(self):
        """get_users returns the registered Workbench users."""
        responses.add(
            responses.POST,
            _api_url("get_users"),
            json={
                "result": [
                    {"username": "user1", "status": "Active", "isAdmin": False, "uid": 1037},
                ]
            },
            status=200,
        )
        users = Users(_FakeContext()).list()
        assert users[0]["username"] == "user1"  # pyright: ignore[reportTypedDictNotRequiredAccess]
