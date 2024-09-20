from typing import List

from .resources import Resource, ResourceParameters, Resources
from .tasks import Task


class Variant(Resource):
    def render(self) -> Task:
        path = f"variants/{self['id']}/render"
        url = self.params.url + path
        response = self.params.session.post(url)
        return Task(self.params, **response.json())


class Variants(Resources):
    def __init__(self, params: ResourceParameters, content_guid: str) -> None:
        super().__init__(params)
        self.content_guid = content_guid

    def find(self) -> List[Variant]:
        path = f"applications/{self.content_guid}/variants"
        url = self.params.url + path
        response = self.params.session.get(url)
        results = response.json() or []
        return [Variant(self.params, **result) for result in results]
