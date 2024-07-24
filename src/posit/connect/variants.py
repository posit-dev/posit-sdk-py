from typing import List

from .resources import Resource, ResourceParameters, Resources
from .tasks import Task


class Variant(Resource):
    @property
    def id(self) -> str:
        return self["id"]

    @property
    def is_default(self) -> bool:
        return self.get("is_default", False)

    def render(self) -> Task:
        path = f"variants/{self.id}/render"
        url = self.url + path
        response = self.session.post(url)
        return Task(self.params, **response.json())


class Variants(Resources):
    def __init__(self, params: ResourceParameters, content_guid: str) -> None:
        super().__init__(params)
        self.content_guid = content_guid

    def find(self) -> List[Variant]:
        path = f"applications/{self.content_guid}/variants"
        url = self.url + path
        response = self.session.get(url)
        results = response.json() or []
        return [Variant(self.params, **result) for result in results]
