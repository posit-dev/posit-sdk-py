from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .context import Context


# Just the same as `.context.py` ContextManager but with `._ctx` attribute, not `.ctx`
class ContextP(Protocol):
    _ctx: Context


class ContentItemP(ContextP, Protocol):
    _path: str


class ContextCls(ContextP):
    """Class that contains the client context."""

    _ctx: Context

    def __init__(self, ctx: Context):
        self._ctx = ctx
