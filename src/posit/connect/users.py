from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List

from requests import Session


from . import urls

from .config import Config
from .paginator import _MAX_PAGE_SIZE, Paginator
from .resources import Resources, Resource


@dataclass(init=False)
class User(Resource):
    guid: str
    email: str
    username: str
    first_name: str
    last_name: str
    user_role: str
    created_time: datetime
    updated_time: datetime
    active_time: datetime
    confirmed: bool
    locked: bool

    # A local shim around locked. This field does not exist in the Connect API.
    is_locked: bool

    @property
    def _compatibility(self):
        return {"locked": "is_locked"}

    @property  # type: ignore
    def locked(self):
        from warnings import warn

        warn(
            "the field 'locked' will be removed in the next major release",
            FutureWarning,
        )
        return self.is_locked

    @locked.setter
    def locked(self, value):
        from warnings import warn

        warn(
            "the field 'locked' will be removed in the next major release",
            FutureWarning,
        )
        self.is_locked = value


class Users(Resources[User]):
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/users")
        self.config = config
        self.session = session

    def find(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> List[User]:
        results = Paginator(self.session, self.url, page_size=page_size).get_all()
        users = (User(**result) for result in results)
        return [user for user in users if filter(user)]

    def find_one(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> User | None:
        pager = Paginator(self.session, self.url, page_size=page_size)
        while pager.total is None or pager.seen < pager.total:
            result = pager.get_next_page()
            for u in result:
                user = User(**u)
                if filter(user):
                    return user
        return None

    def get(self, id: str) -> User:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        return User(**response.json())

    def create(self) -> User:
        raise NotImplementedError()

    def update(self) -> User:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()
