from typing_extensions import List

from .context import Context
from .resources import BaseResource, Resources
from .tasks import Task


class Variant(BaseResource):
    def render(self) -> Task:
        path = f"variants/{self['id']}/render"
        response = self._ctx.client.post(path)
        return Task(self._ctx, **response.json())


class Variants(Resources):
    def __init__(self, ctx: Context, content_guid: str) -> None:
        super().__init__(ctx)
        self.content_guid = content_guid

    def find(self) -> List[Variant]:
        path = f"applications/{self.content_guid}/variants"
        response = self._ctx.client.get(path)
        results = response.json() or []
        return [Variant(self._ctx, **result) for result in results]
