from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    from .context import Context

# Any subclass of Context should be able to be used where Context is expected
ContextT = TypeVar("ContextT", bound="Context", covariant=True)


# Just the same as `.context.py` ContextManager but with `._ctx` attribute, not `.ctx`
class ContextP(Generic[ContextT], Protocol):
    _ctx: ContextT
