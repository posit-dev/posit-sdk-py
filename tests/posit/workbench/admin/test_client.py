"""Tests for the Bearer-token Workbench launcher API client."""

import json
from unittest.mock import MagicMock

import responses

from posit.workbench.admin import Client

SERVER_URL = "https://workbench.example.com"
API_KEY = "test-token"


def _client() -> Client:
    return Client(url=SERVER_URL, api_key=API_KEY)


def _api_url(method: str) -> str:
    return f"{SERVER_URL}/api/{method}"


class TestAuth:
    """Tests for Bearer-token authentication."""

    @responses.activate
    def test_sends_bearer_token(self):
        """Requests carry an Authorization: Bearer <token> header."""
        responses.add(responses.POST, _api_url("version"), json={"version": {}}, status=200)
        _client().call_raw("version")
        assert responses.calls[0].request.headers["Authorization"] == f"Bearer {API_KEY}"


class TestVersion:
    """Tests for the bare (non-`{"result": ...}`-wrapped) version response."""

    @responses.activate
    def test_version_property_returns_dict(self):
        """client.version returns the raw structured version dict."""
        responses.add(
            responses.POST,
            _api_url("version"),
            json={"version": {"major": "2025", "minor": "12"}, "features": ["jobs"]},
            status=200,
        )
        assert _client().version == {"major": "2025", "minor": "12"}

    @responses.activate
    def test_context_version_returns_dotted_string(self):
        """Context.version joins major.minor.patch into a requires()-compatible string."""
        responses.add(
            responses.POST,
            _api_url("version"),
            json={"version": {"major": "2026", "minor": "7", "patch": "0"}, "features": []},
            status=200,
        )
        client = _client()
        assert client._ctx.version == "2026.7.0"


class TestTimeout:
    """Tests for the default per-request timeout."""

    def test_default_timeout_is_applied(self):
        """The configured timeout is passed to the underlying session call."""
        client = _client()
        client.session.post = MagicMock()

        client.post("api/version", json={"method": "version", "kwparams": {}})

        _, kwargs = client.session.post.call_args
        assert kwargs["timeout"] == 30

    def test_per_call_timeout_overrides_default(self):
        """An explicit timeout kwarg overrides the client's default."""
        client = _client()
        client.session.post = MagicMock()

        client.post("api/version", json={"method": "version", "kwparams": {}}, timeout=1)

        _, kwargs = client.session.post.call_args
        assert kwargs["timeout"] == 1


class TestCallHelpers:
    """Tests that the client's call()/call_stream()/call_raw() delegate to rpc.py."""

    @responses.activate
    def test_call_sends_method_and_kwparams(self):
        """call() posts the JSON-RPC envelope and unwraps the result."""
        responses.add(responses.POST, _api_url("stop_job"), json={"result": None}, status=200)
        _client().call("stop_job", job_id="abc123", force_quit=None)
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body == {"method": "stop_job", "kwparams": {"job_id": "abc123"}}
