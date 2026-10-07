"""Tests for the shared Sessions resource manager."""

import json

import responses

from posit.workbench.sessions import Sessions
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


def _sessions() -> Sessions:
    return Sessions(_FakeContext())


class TestLaunch:
    """Tests for Sessions.launch()."""

    @responses.activate
    def test_launch(self):
        """A launch_session call returns the new session's id/url/project_id."""
        responses.add(
            responses.POST,
            _api_url("launch_session"),
            json={
                "result": {
                    "url": "/s/0da29cfc78a31acdd5861/",
                    "id": "acdd5861",
                    "project_id": "cfc78a31",
                }
            },
            status=200,
        )
        result = _sessions().launch(
            "RStudio",
            name="My RStudio Session",
            launch_parameters={"name": "Job name", "cluster": "Local"},
        )
        assert result["id"] == "acdd5861"  # pyright: ignore[reportTypedDictNotRequiredAccess]

        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["method"] == "launch_session"
        assert body["kwparams"]["workbench"] == "RStudio"
        assert "username" not in body["kwparams"]


class TestResume:
    """Tests for Sessions.resume()."""

    @responses.activate
    def test_resume(self):
        """A resume_session call returns the session's id/url/project_id."""
        responses.add(
            responses.POST,
            _api_url("resume_session"),
            json={
                "result": {
                    "url": "/s/0da29cfc78a31acdd5861/",
                    "id": "acdd5861",
                    "project_id": "cfc78a31",
                }
            },
            status=200,
        )
        result = _sessions().resume("93022e28")
        assert result["project_id"] == "cfc78a31"  # pyright: ignore[reportTypedDictNotRequiredAccess]


class TestGet:
    """Tests for Sessions.get()."""

    @responses.activate
    def test_get_with_no_params_returns_all_sessions(self):
        """With no session_id, get() returns all of the caller's sessions."""
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={
                "result": {
                    "sessions": [
                        {
                            "url": "/s/0da29cfc78a316124d41f/",
                            "id": "6124d41f",
                            "activity_state": "suspended",
                            "workbench": "RStudio",
                        }
                    ]
                }
            },
            status=200,
        )
        result = _sessions().get()
        assert result["sessions"][0]["id"] == "6124d41f"  # pyright: ignore[reportTypedDictNotRequiredAccess]
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["kwparams"] == {}

    @responses.activate
    def test_get_joins_list_of_session_ids(self):
        """A list of session_id values is comma-joined for the request."""
        responses.add(responses.POST, _api_url("get_session"), json={"result": {}}, status=200)
        _sessions().get(["id1", "id2"])
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["kwparams"]["session_id"] == "id1,id2"


class TestGetHistorical:
    """Tests for Sessions.get_historical()."""

    @responses.activate
    def test_get_historical(self):
        """get_historical_session returns ended sessions, optionally filtered by time range."""
        responses.add(
            responses.POST,
            _api_url("get_historical_session"),
            json={
                "result": {
                    "sessions": [
                        {
                            "id": "d1552b86",
                            "username": "user1",
                            "workbench": "VS Code",
                        }
                    ]
                }
            },
            status=200,
        )
        result = _sessions().get_historical(
            filter_time_begin="2025-07-23T00:00:00.000000Z",
            filter_time_end="2025-07-30T23:59:59.999999Z",
        )
        assert result["sessions"][0]["username"] == "user1"  # pyright: ignore[reportTypedDictNotRequiredAccess]


class TestStop:
    """Tests for Sessions.stop()."""

    @responses.activate
    def test_stop_joins_list_of_session_ids(self):
        """A list of session_ids is comma-joined, and options pass through."""
        responses.add(responses.POST, _api_url("stop_session"), json={"result": None}, status=200)
        _sessions().stop(["id1", "id2"], force_quit=True)
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["kwparams"] == {"session_ids": "id1,id2", "force_quit": True}


class TestConnectionUrl:
    """Tests for Sessions.connection_url()."""

    def test_connection_url_resolves_relative_url(self):
        """The session's relative url is resolved against the client's server_url."""
        session = {"url": "/s/0da29cfc78a31acdd5861/"}
        assert (
            _sessions().connection_url(session)
            == "https://workbench.example.com/s/0da29cfc78a31acdd5861"
        )
