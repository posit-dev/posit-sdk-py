"""Integration tests for ``posit.connect.sessions.Session``.

These tests exercise the real ``requests`` / ``urllib3`` / socket stack
against a local HTTP server, rather than monkey-patching ``HTTPAdapter.send``
the way unit tests with ``responses`` do. That lets us verify that the
redirect semantics we rely on (POST body preservation on 301/302,
``Authorization`` stripping on cross-origin hops, ``response.history``
population, ``TooManyRedirects`` on overflow) actually hold end-to-end.

The server is an in-process ``http.server`` instance on ``127.0.0.1`` — no
Connect instance is required, so these run in any environment.
"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, List, Tuple

import pytest
import requests

from posit.connect.sessions import Session


class _Recorder:
    """Shared state between the test and the request handler thread."""

    def __init__(self) -> None:
        self.requests: List[Tuple[str, str, dict, bytes]] = []  # method, path, headers, body
        self.responder: Callable[[BaseHTTPRequestHandler], None] | None = None


def _make_handler(recorder: _Recorder):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):  # noqa: A002 - silence default stderr logging
            pass

        def _record(self) -> None:
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else b""
            recorder.requests.append(
                (self.command, self.path, dict(self.headers), body),
            )

        def do_GET(self) -> None:  # noqa: N802
            self._record()
            assert recorder.responder is not None
            recorder.responder(self)

        def do_POST(self) -> None:  # noqa: N802
            self._record()
            assert recorder.responder is not None
            recorder.responder(self)

    return Handler


@pytest.fixture
def server():
    recorder = _Recorder()
    httpd = HTTPServer(("127.0.0.1", 0), _make_handler(recorder))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address
    base = f"http://{host}:{port}"
    try:
        yield base, recorder
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def _ok(handler: BaseHTTPRequestHandler) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", "2")
    handler.end_headers()
    handler.wfile.write(b"{}")


def _redirect(status: int, location: str) -> Callable[[BaseHTTPRequestHandler], None]:
    def respond(handler: BaseHTTPRequestHandler) -> None:
        handler.send_response(status)
        handler.send_header("Location", location)
        handler.send_header("Content-Length", "0")
        handler.end_headers()

    return respond


def test_post_preserves_body_across_302(server):
    """A POST that 302s to a new path re-POSTs the body (libcurl POSTREDIR)."""
    base, recorder = server
    hops = iter([_redirect(302, "/next"), _ok])
    recorder.responder = lambda h: next(hops)(h)

    session = Session()
    response = session.post(f"{base}/start", data=b"payload-bytes", preserve_post=True)

    assert response.status_code == 200
    assert len(recorder.requests) == 2
    assert recorder.requests[0][0] == "POST"
    assert recorder.requests[0][3] == b"payload-bytes"
    assert recorder.requests[1][0] == "POST"
    assert recorder.requests[1][3] == b"payload-bytes"
    # response.history should carry the 302 hop.
    assert [r.status_code for r in response.history] == [302]


def test_post_downgrades_to_get_when_preserve_post_false(server):
    base, recorder = server
    hops = iter([_redirect(302, "/next"), _ok])
    recorder.responder = lambda h: next(hops)(h)

    session = Session()
    response = session.post(f"{base}/start", data=b"payload", preserve_post=False)

    assert response.status_code == 200
    assert recorder.requests[0][0] == "POST"
    assert recorder.requests[1][0] == "GET"
    assert recorder.requests[1][3] == b""  # body dropped on downgrade


@pytest.mark.parametrize("status", [307, 308])
def test_post_preserves_method_on_307_308(server, status):
    base, recorder = server
    hops = iter([_redirect(status, "/next"), _ok])
    recorder.responder = lambda h: next(hops)(h)

    session = Session()
    response = session.post(f"{base}/start", data=b"payload", preserve_post=False)

    assert response.status_code == 200
    assert recorder.requests[1][0] == "POST"
    assert recorder.requests[1][3] == b"payload"


def test_cross_origin_redirect_strips_authorization(server):
    """A cross-origin redirect must not forward the Authorization header.

    We use ``127.0.0.1`` as the request origin and redirect to ``localhost``
    on the same port — different hostnames, so ``rebuild_auth`` must strip
    the session-level Authorization header on the follow-up hop.
    """
    base, recorder = server
    _, port = base.rsplit(":", 1)
    cross_origin_next = f"http://localhost:{port}/collect"

    hops = iter([_redirect(302, cross_origin_next), _ok])
    recorder.responder = lambda h: next(hops)(h)

    session = Session()
    session.headers["Authorization"] = "Key super-secret-token"
    session.post(f"{base}/start", data=b"payload", preserve_post=True)

    assert len(recorder.requests) == 2
    assert recorder.requests[0][2].get("Authorization") == "Key super-secret-token"
    # The cross-origin second hop must NOT carry the Authorization header.
    assert "Authorization" not in recorder.requests[1][2]
    assert "authorization" not in {k.lower() for k in recorder.requests[1][2]}


def test_same_origin_redirect_preserves_authorization(server):
    base, recorder = server
    hops = iter([_redirect(302, "/next"), _ok])
    recorder.responder = lambda h: next(hops)(h)

    session = Session()
    session.headers["Authorization"] = "Key super-secret-token"
    session.post(f"{base}/start", data=b"payload", preserve_post=True)

    assert len(recorder.requests) == 2
    assert recorder.requests[0][2].get("Authorization") == "Key super-secret-token"
    assert recorder.requests[1][2].get("Authorization") == "Key super-secret-token"


def test_max_redirects_raises_too_many_redirects(server):
    base, recorder = server
    recorder.responder = _redirect(302, "/loop")

    session = Session()
    with pytest.raises(requests.exceptions.TooManyRedirects):
        session.post(f"{base}/start", data=b"payload", max_redirects=3, preserve_post=True)

    # Initial POST + 3 followed redirects before requests raises.
    assert len(recorder.requests) == 4
