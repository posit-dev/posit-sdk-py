"""Low-level JSON-RPC call helpers for the Workbench launcher API.

Every launcher API method is invoked as ``POST /api/<method>`` with a body of
``{"method": <method>, "kwparams": {...}}``. A successful call returns HTTP 200 with
``{"result": ...}``; an application-level failure still returns HTTP 200 but with
``{"error": {"code": ..., "message": ...}}``. Two methods (``get_job_output`` and
``get_audited_job_output``) stream newline-delimited JSON objects instead of a single body.

These functions only ever call ``client.post()`` -- they make no assumptions about how auth got
attached to the underlying session, so they're shared by both the cookie-authenticated
`posit.workbench.Client` and the Bearer-token `posit.workbench.admin.Client`.
"""

from __future__ import annotations

import json
from requests import HTTPError, Response
from typing_extensions import Any, Iterator, Protocol

from .errors import WorkbenchHTTPError, WorkbenchRPCError


class _ClientProtocol(Protocol):
    """Structural stand-in for whichever concrete Client is calling these functions.

    Deliberately minimal -- only what call()/call_stream()/call_raw() actually need. Callers
    needing more (e.g. Sessions.connection_url() needing ``server_url``) should not widen this;
    see that call site for how it's handled instead.
    """

    def post(self, path: str, **kwargs: Any) -> Response: ...


class ContextProtocol(Protocol):
    """Structural stand-in for whichever concrete Context a resource manager holds.

    ``posit.workbench.context.Context`` (env-var-based) and
    ``posit.workbench.admin.context.Context`` (HTTP-fetched) are unrelated classes, so the
    shared resource managers (sessions.py, jobs.py, etc.) type their ``ctx`` parameter as this
    Protocol instead of either concrete class. ``client`` is declared as a read-only property
    (not a plain attribute) so structural matching is covariant, not invariant -- otherwise
    neither concrete ``Context``'s ``client: Client`` would satisfy this Protocol, since each
    ``Client`` is a narrower type than ``_ClientProtocol``.
    """

    @property
    def client(self) -> _ClientProtocol: ...


def _kwparams(**kwparams: Any) -> dict[str, Any]:
    return {k: v for k, v in kwparams.items() if v is not None}


def _raise_for_status(response: Response) -> None:
    try:
        response.raise_for_status()
    except HTTPError as e:
        body: Any
        try:
            body = response.json()
        except ValueError:
            body = response.text
        raise WorkbenchHTTPError(response.status_code, body) from e


def _unwrap(body: dict[str, Any]) -> Any:
    if "error" in body:
        error = body["error"]
        raise WorkbenchRPCError(error.get("code"), error.get("message"))
    return body.get("result")


def call(client: _ClientProtocol, method: str, **kwparams: Any) -> Any:
    """Invoke a non-streaming launcher API method and return its ``result``."""
    response = client.post(
        f"api/{method}",
        json={"method": method, "kwparams": _kwparams(**kwparams)},
    )
    _raise_for_status(response)
    return _unwrap(response.json())


def call_raw(client: _ClientProtocol, method: str, **kwparams: Any) -> dict[str, Any]:
    """Invoke a method whose success response is NOT wrapped in ``{"result": ...}``.

    Confirmed against a live server: unlike every other method, ``version`` returns its
    payload bare (``{"version": {...}, "features": [...]}``), not
    ``{"result": {"version": {...}, ...}}``. Still checks for the standard
    ``{"error": {...}}`` envelope, in case that part of the contract holds even here.
    """
    response = client.post(
        f"api/{method}",
        json={"method": method, "kwparams": _kwparams(**kwparams)},
    )
    _raise_for_status(response)
    body = response.json()
    if "error" in body:
        error = body["error"]
        raise WorkbenchRPCError(error.get("code"), error.get("message"))
    return body


def call_stream(client: _ClientProtocol, method: str, **kwparams: Any) -> Iterator[dict[str, Any]]:
    """Invoke a streaming launcher API method, yielding each newline-delimited JSON chunk.

    Assumes each JSON object is emitted compactly on its own line (standard JSON-lines
    framing); the doc's pretty-printed examples are for readability only.
    """
    response = client.post(
        f"api/{method}",
        json={"method": method, "kwparams": _kwparams(**kwparams)},
        stream=True,
    )
    try:
        _raise_for_status(response)
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            chunk = json.loads(line)
            if isinstance(chunk, dict) and "error" in chunk:
                error = chunk["error"]
                raise WorkbenchRPCError(error.get("code"), error.get("message"))
            yield chunk
    finally:
        response.close()
