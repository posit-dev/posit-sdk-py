from typing import List

from ._active import ResourceDict
from .resources import (
    ResourceParameters,
    Resources,
    context_to_resource_parameters,
    resource_parameters_to_context,
)
from .tasks import Task


class Variant(ResourceDict):
    def render(self) -> Task:
        # TODO Move to within Task logic?
        path = f"variants/{self['id']}/render"
        url = self._ctx.url + path
        response = self._ctx.session.post(url)
        return Task(context_to_resource_parameters(self._ctx), **response.json())


# TODO; Inherit from ActiveList
class Variants(Resources):
    def __init__(self, params: ResourceParameters, content_guid: str) -> None:
        super().__init__(params)
        self.content_guid = content_guid

    def find(self) -> List[Variant]:
        path = f"applications/{self.content_guid}/variants"
        url = self.params.url + path
        response = self.params.session.get(url)
        results = response.json() or []
        return [
            Variant(resource_parameters_to_context(self.params), **result) for result in results
        ]
