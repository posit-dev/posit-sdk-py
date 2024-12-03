from typing import List

from ._active import ResourceDict
from ._types_content_item import ContentItemContext
from ._types_context import ContextP
from .tasks import Task


class Variant(ResourceDict):
    def render(self) -> Task:
        path = f"variants/{self['id']}/render"
        url = self._ctx.url + path
        response = self._ctx.session.post(url)
        return Task(self._ctx, **response.json())


# No special inheritance as it is a placeholder class
class Variants(ContextP[ContentItemContext]):
    def __init__(self, ctx: ContentItemContext) -> None:
        super().__init__()
        self._ctx = ctx

    def find(self) -> List[Variant]:
        path = f"applications/{self._ctx.content_guid}/variants"
        url = self._ctx.url + path
        response = self._ctx.session.get(url)
        results = response.json() or []
        return [Variant(self._ctx, **result) for result in results]
