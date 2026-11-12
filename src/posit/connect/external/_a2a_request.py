"""Request state for an A2A turn, shared by the A2A server and the tools that run inside it.

This module does not import ``a2a-sdk``, so tools that run inside a turn can read the current
request without the A2A extra installed.
"""

from __future__ import annotations

import base64
import json
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from typing_extensions import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping


@dataclass(frozen=True)
class A2ARequest:
    """The A2A request that starts or continues an agent turn.

    Attributes
    ----------
    context_id
        The context ID. The request's own ID is used when it has one. Otherwise the server
        generates a UUID version 4.
    user_session_token
        The value of the ``Posit-Connect-User-Session-Token`` request header, if present.
    visitor_guid
        The ``sub`` claim of the session token, if the token is present and well formed.
    headers
        The request headers with lower-cased names. Only these headers are kept:
        ``posit-connect-user-session-token``, ``rstudio-connect-credentials``,
        ``rstudio-connect-app-base-url``, ``a2a-version``, ``user-agent``, and ``accept-language``.
    """

    context_id: str
    user_session_token: str | None
    visitor_guid: str | None
    headers: Mapping[str, str]


_CURRENT: ContextVar[A2ARequest | None] = ContextVar("commons_a2a_request", default=None)


def current_a2a_request() -> A2ARequest | None:
    """Return the A2A request whose agent turn is running, or None outside a turn.

    A tool that needs the visitor's credentials must call this at call time. The agent is reused
    across messages in one context, so a request captured earlier can hold an expired token.
    """
    return _CURRENT.get()


@contextmanager
def _request_scope(request: A2ARequest) -> Iterator[None]:
    token = _CURRENT.set(request)
    try:
        yield
    finally:
        _CURRENT.reset(token)


def visitor_guid_from_token(token: str | None) -> str | None:
    """Return the ``sub`` claim of a Connect user session token, or None.

    The signature is not checked. Connect deletes any client-supplied copy of the header and sets
    its own, so inside Connect the claims are trusted. A malformed token has no visitor.
    """
    if not token:
        return None
    segments = token.split(".")
    if len(segments) != 3:
        return None
    payload = segments[1]
    try:
        claims: Any = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except ValueError:
        return None
    subject = claims.get("sub") if isinstance(claims, dict) else None
    return subject if isinstance(subject, str) and subject else None
