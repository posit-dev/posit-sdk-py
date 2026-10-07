"""Tests for the shared launcher API JSON-RPC call helpers."""

import json

import pytest
import responses

from posit.workbench import rpc
from posit.workbench.errors import WorkbenchHTTPError, WorkbenchRPCError


class _FakeClient:
    """Minimal stand-in exposing just ``.post()``, matching ``rpc._ClientProtocol``."""

    def __init__(self, server_url: str = "https://workbench.example.com"):
        import requests

        self.server_url = server_url
        self.session = requests.Session()

    def post(self, path, **kwargs):
        """Post to the fake server, joining the base URL and path."""
        return self.session.post(f"{self.server_url}/{path}", **kwargs)


def _api_url(method: str) -> str:
    return f"https://workbench.example.com/api/{method}"


class TestCall:
    """Tests for the non-streaming ``call()`` helper."""

    @responses.activate
    def test_returns_result(self):
        """A `{"result": ...}` envelope is unwrapped."""
        responses.add(
            responses.POST,
            _api_url("get_compute_envs"),
            json={"result": {"clusters": []}},
            status=200,
        )
        result = rpc.call(_FakeClient(), "get_compute_envs")
        assert result == {"clusters": []}

    @responses.activate
    def test_sends_method_and_kwparams(self):
        """The request body carries the method name and non-None kwparams."""
        responses.add(responses.POST, _api_url("stop_job"), json={"result": None}, status=200)
        rpc.call(_FakeClient(), "stop_job", job_id="abc123", force_quit=None)
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body == {"method": "stop_job", "kwparams": {"job_id": "abc123"}}

    @responses.activate
    def test_raises_rpc_error_on_error_envelope(self):
        """A `{"error": ...}` envelope raises WorkbenchRPCError."""
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={"error": {"code": 401, "message": "Permission denied"}},
            status=200,
        )
        with pytest.raises(WorkbenchRPCError) as exc_info:
            rpc.call(_FakeClient(), "get_session")
        assert exc_info.value.code == 401
        assert exc_info.value.message == "Permission denied"

    @responses.activate
    def test_raises_http_error_on_non_2xx(self):
        """A non-2xx HTTP status raises WorkbenchHTTPError."""
        responses.add(
            responses.POST,
            _api_url("get_users"),
            json={"error": {"code": 401, "message": "unauthorized"}},
            status=401,
        )
        with pytest.raises(WorkbenchHTTPError) as exc_info:
            rpc.call(_FakeClient(), "get_users")
        assert exc_info.value.status_code == 401


class TestCallRaw:
    """Tests for ``call_raw()``, used by methods that don't wrap their response in "result"."""

    @responses.activate
    def test_returns_bare_body(self):
        """``version`` returns its payload bare, not wrapped in `{"result": ...}`."""
        responses.add(
            responses.POST,
            _api_url("version"),
            json={"version": {"major": "2026"}, "features": ["jobs"]},
            status=200,
        )
        result = rpc.call_raw(_FakeClient(), "version")
        assert result == {"version": {"major": "2026"}, "features": ["jobs"]}

    @responses.activate
    def test_raises_rpc_error_on_error_envelope(self):
        """A `{"error": ...}` envelope still raises WorkbenchRPCError."""
        responses.add(
            responses.POST,
            _api_url("version"),
            json={"error": {"code": 401, "message": "Permission denied"}},
            status=200,
        )
        with pytest.raises(WorkbenchRPCError) as exc_info:
            rpc.call_raw(_FakeClient(), "version")
        assert exc_info.value.code == 401


class TestCallStream:
    """Tests for the streaming ``call_stream()`` helper."""

    @responses.activate
    def test_yields_each_json_line(self):
        """Each newline-delimited JSON object is yielded as a chunk."""
        body = "\n".join(
            [
                json.dumps({"jobId": "j1", "outputType": "stdout", "output": "hello "}),
                json.dumps({"jobId": "j1", "outputType": "stdout", "output": "world"}),
            ]
        )
        responses.add(responses.POST, _api_url("get_job_output"), body=body, status=200)
        chunks = list(rpc.call_stream(_FakeClient(), "get_job_output", job_id="j1"))
        assert chunks == [
            {"jobId": "j1", "outputType": "stdout", "output": "hello "},
            {"jobId": "j1", "outputType": "stdout", "output": "world"},
        ]

    @responses.activate
    def test_raises_on_error_chunk(self):
        """An `{"error": ...}` chunk mid-stream raises WorkbenchRPCError."""
        body = json.dumps({"error": {"code": 404, "message": "job not found"}})
        responses.add(responses.POST, _api_url("get_job_output"), body=body, status=200)
        with pytest.raises(WorkbenchRPCError) as exc_info:
            list(rpc.call_stream(_FakeClient(), "get_job_output", job_id="missing"))
        assert exc_info.value.code == 404
