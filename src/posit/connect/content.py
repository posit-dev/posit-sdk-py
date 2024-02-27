from __future__ import annotations

from typing import Callable, List, Optional, TypedDict

from requests import Session

from . import urls

from .config import Config
from .paginator import _MAX_PAGE_SIZE, Paginator


class ContentItem(TypedDict, total=False):
    # TODO: specify types
    pass


class Content:
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/content")
        self.config = config
        self.session = session

    def find(
        self,
        filter: Callable[[ContentItem], bool] = lambda _: True,
        query: Optional[str] = None,
        page_size=_MAX_PAGE_SIZE,
    ) -> List[ContentItem]:
        if query:
            # TODO: check connect_version, error if too old
            results = Paginator(
                self.session,
                urls.append_path(self.config.url, "v1/search/content"),
                page_size=page_size,
                params={"q": query},
            ).get_all()
        else:
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
