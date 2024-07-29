from typing import List

from requests import Session

from .config import Config
from .resources import Resource, Resources
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
        url = self.config.url + path
        response = self.session.post(url)
        return Task(self.config, self.session, **response.json())


class Variants(Resources):
    def __init__(
        self, config: Config, session: Session, content_guid: str
    ) -> None:
        super().__init__(config, session)
        self.content_guid = content_guid

    def find(self) -> List[Variant]:
        path = f"applications/{self.content_guid}/variants"
        url = self.config.url + path
        response = self.session.get(url)
        results = response.json() or []
        return [
            Variant(self.config, self.session, **result) for result in results
        ]
