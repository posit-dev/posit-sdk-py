from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional, TypedDict

from requests import Session

from . import urls

from .config import Config
from .paginator import Paginator


class Group(TypedDict, total=False):
    guid: str
    email: str
    groupname: str
    first_name: str
    last_name: str
    group_role: str
    created_time: datetime
    updated_time: datetime
    active_time: datetime
    confirmed: bool
    locked: bool


_MAX_PAGE_SIZE = 500


class Groups(Paginator):
    def __init__(self, config: Config, session: Session) -> None:
        super().__init__(
            session, urls.append_path(config.url, "v1/groups"), page_size=_MAX_PAGE_SIZE
        )
        self.config = config
        self.session = session

    # todo - replace with query parameter based filtering.
    # reason - the current implementation is a fill in for actual implementation
    def find(
        self,
        filter: Callable[[Group], bool] = lambda group: True,
        *,
        page_size: int = _MAX_PAGE_SIZE,
    ) -> list[Group]:
        url = urls.append_path(self.config.url, "v1/groups")
        paginator = Paginator(self.session, url, page_size=page_size)
        groups = (Group(**group) for group in paginator)
        return [group for group in groups if filter(group)]

    # todo - replace with query parameter based filtering.
    # reason - the current implementation is a fill in for actual implementation
    def find_one(
        self,
        filter: Callable[[Group], bool] = lambda group: True,
        *,
        page_size: int = _MAX_PAGE_SIZE,
    ) -> Optional[Group]:
        # note - you may be tempted to to use self.find(filter, page_size) and return the first element.
        # note - this is less efficient as it will fetch all the groups and then filter them.
        # note - instead, we use the paginator directly to fetch the first group that matches the filter.
        # note - since the paginator fetches the groups in pages, it will stop fetching once it finds a match.
        url = urls.append_path(self.config.url, "v1/groups")
        paginator = Paginator(self.session, url, page_size=page_size)
        groups = (Group(**group) for group in paginator)
        groups = (group for group in groups if filter(group))
        return next(groups, None)

    def get(self, id: str) -> Group:
        url = urls.append_path(self.config.url, "v1/groups", id)
        response = self.session.get(url)
        return Group(**response.json())
