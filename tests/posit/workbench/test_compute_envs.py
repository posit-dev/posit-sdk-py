"""Tests for the shared ComputeEnvs resource manager."""

import responses

from posit.workbench.compute_envs import ComputeEnvs
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


class TestList:
    """Tests for ComputeEnvs.list()."""

    @responses.activate
    def test_list(self):
        """get_compute_envs returns the clusters and per-IDE defaults."""
        responses.add(
            responses.POST,
            _api_url("get_compute_envs"),
            json={
                "result": {
                    "clusters": [{"name": "Local", "type": "Local"}],
                    "workbenches": {"RStudio": {"default_cluster": "Localhost"}},
                }
            },
            status=200,
        )
        result = ComputeEnvs(_FakeContext()).list()
        assert result["clusters"][0]["name"] == "Local"  # pyright: ignore[reportTypedDictNotRequiredAccess]
