"""Context for the Bearer-token Workbench launcher API client.

The parent package's ``posit.workbench.context.requires(version)`` decorator is reused as-is by
this client -- it's generic over any ``instance._ctx.version`` string, and doesn't care how that
string is produced.

But this client needs its own ``Context``, since the parent's reads the ``RSTUDIO_VERSION``
env var (only set inside a session -- not applicable when using a Bearer token from outside
one). This one instead fetches the version from the live ``version`` launcher API method,
modeled on ``posit.connect.context.Context``'s HTTP-fetched, lazily-cached version.
"""

from __future__ import annotations

import weakref

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class Context:
    """Holds a weak reference to the client and lazily fetches/caches the server version."""

    def __init__(self, client: Client):
        # Since this is a child object of the client, we use a weak reference to avoid circular
        # references (which would prevent garbage collection)
        self.client: Client = weakref.proxy(client)

    @property
    def version(self) -> str | None:
        """The server version as a plain ``major.minor.patch`` string.

        Distinct from ``Client.version`` (the public, dict-returning property -- e.g.
        ``{"major": "2025", "minor": "12"}``): this one exists purely to feed the shared
        ``requires()`` decorator, which needs a ``packaging.version.Version``-parseable
        string, not the raw structured dict. Sourced from the same bare (not
        ``{"result": ...}``-wrapped, see ``rpc.call_raw``) ``version`` response.
        """
        if not hasattr(self, "_version"):
            info = self.client.call_raw("version")
            v = info.get("version") or {}
            major = v.get("major")
            self._version = f"{major}.{v.get('minor')}.{v.get('patch', '0')}" if major else None
        return self._version

    @version.setter
    def version(self, value: str | None) -> None:
        self._version = value
