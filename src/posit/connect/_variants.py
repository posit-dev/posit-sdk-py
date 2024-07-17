from typing import List
from requests import Session

from . import urls
from .config import Config
from .resources import Resource, Resources


class _Variant(Resource):
    @property
    def id(self) -> str:
        return self["id"]

    @property
    def is_default(self) -> bool:
        return self.get("is_default", False)

    def render(self) -> None:
        path = f"variants/{self.id}/render"
        url = urls.append(self.config.url, path)
        self.session.post(url)


class _Variants(Resources):
    def __init__(
        self, config: Config, session: Session, content_guid: str
    ) -> None:
        super().__init__(config, session)
        self.content_guid = content_guid

    def find(self) -> List[_Variant]:
        path = f"applications/{self.content_guid}/variants"
        url = urls.append(self.config.url, path)
        response = self.session.get(url)
        results = response.json()
        return [
            _Variant(self.config, self.session, **result) for result in results
        ]
