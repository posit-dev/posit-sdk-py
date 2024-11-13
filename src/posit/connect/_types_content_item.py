from __future__ import annotations

from typing import Protocol

from ._active import ActiveDict, ResourceDict
from ._types_context import ContextP
from .context import Context


class ContentItemP(ContextP["ContentItemContext"], Protocol):
    _ctx: ContentItemContext


class ContentItemResourceDict(ResourceDict["ContentItemContext"], ContentItemP):
    pass


class ContentItemActiveDict(ActiveDict["ContentItemContext"], ContentItemP):
    pass


class ContentItemContext(Context):
    content_guid: str
    content_path: str

    def __init__(self, ctx: Context, *, content_guid: str) -> None:
        super().__init__(ctx.session, ctx.url)
        self.content_guid = content_guid
        content_path = f"v1/content/{content_guid}"
        self.content_path = content_path
