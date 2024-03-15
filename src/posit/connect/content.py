from __future__ import annotations

from typing import Callable, List, Optional

from requests import Session

from . import urls

from .config import Config
from .resources import Resources


class ContentItem(dict):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # TODO: self.url, self.config, self.session

    def update(self):
        pass

    @property
    def name(self) -> str:
        return self["name"]

    @property
    def id(self) -> str:
        return self["id"]

    @property
    def title(self) -> str:
        return self["title"]

    @property
    def description(self) -> str:
        return self["description"]

    @property
    def created_time(self) -> str:
        return self["created_time"]

    @property
    def guid(self) -> str:
        return self["guid"]

    @property
    def access_type(self) -> str:
        return self["access_type"]

    @property
    def connection_timeout(self) -> Optional[int]:
        return self["connection_timeout"]


class Content(Resources[ContentItem]):
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/content")
        self.config = config
        self.session = session

    def find(
        self, filter: Callable[[ContentItem], bool] = lambda _: True
    ) -> List[ContentItem]:
        results = self.session.get(self.url).json()
        return [ContentItem(**c) for c in results if filter(ContentItem(**c))]

    def find_one(
        self, filter: Callable[[ContentItem], bool] = lambda _: True
    ) -> ContentItem | None:
        results = self.session.get(self.url).json()
        for c in results:
            content_item = ContentItem(**c)
            if filter(content_item):
                return content_item
        return None

    def get(self, id: str) -> ContentItem:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        return ContentItem(**response.json())

    def create(self) -> ContentItem:
        raise NotImplementedError()

    def update(self) -> ContentItem:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()
