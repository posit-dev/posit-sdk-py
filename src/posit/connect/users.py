from __future__ import annotations
from typing import Callable, List, Optional


import requests


from . import urls

from .config import Config
from .paginator import _MAX_PAGE_SIZE, Paginator
from .resources import Resource, Resources


class User(Resource):
    @property
    def guid(self) -> str:
        return self.get("guid")  # type: ignore

    @property
    def email(self) -> str:
        return self.get("email")  # type: ignore

    @property
    def username(self) -> str:
        return self.get("username")  # type: ignore

    @property
    def first_name(self) -> str:
        return self.get("first_name")  # type: ignore

    @property
    def last_name(self) -> str:
        return self.get("last_name")  # type: ignore

    @property
    def user_role(self) -> str:
        return self.get("user_role")  # type: ignore

    @property
    def created_time(self) -> str:
        return self.get("created_time")  # type: ignore

    @property
    def updated_time(self) -> str:
        return self.get("updated_time")  # type: ignore

    @property
    def active_time(self) -> str:
        return self.get("active_time")  # type: ignore

    @property
    def confirmed(self) -> bool:
        return self.get("confirmed")  # type: ignore

    @property
    def locked(self) -> bool:
        return self.get("locked")  # type: ignore

    def _update(self, body):
        self.session.patch(self.url, json=body)
        # If the request is successful, update the local object
        super().update(body)
        # TODO(#99): that patch request returns a payload on success,
        # so we should instead update the local object with that payload
        # (includes updated_time)

    def update(  # type: ignore
        self,
        # Not all properties are settable, so we enumerate them here
        # (also for type-hinting purposes)
        email: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        user_role: Optional[str] = None,
        # TODO(#100): in the API, this goes via POST /v1/users/{guid}/lock
        # accept it here and make that request? Or add a .lock() method?
        # locked: Optional[bool] = None,
    ) -> None:
        kwargs = {}
        if email is not None:
            kwargs["email"] = email
        if username is not None:
            kwargs["username"] = username
        if first_name is not None:
            kwargs["first_name"] = first_name
        if last_name is not None:
            kwargs["last_name"] = last_name
        if user_role is not None:
            kwargs["user_role"] = user_role
        # if locked is not None:
        #     kwargs["locked"] = locked
        self._update(kwargs)


class Users(Resources[User]):
    def __init__(self, config: Config, session: requests.Session) -> None:
        self.url = urls.append_path(config.url, "v1/users")
        self.config = config
        self.session = session

    def find(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> List[User]:
        results = Paginator(self.session, self.url, page_size=page_size).get_all()
        users = (
            User(
                session=self.session,
                url=urls.append_path(self.url, user["guid"]),
                **user,
            )
            for user in results
        )
        return [user for user in users if filter(user)]

    def find_one(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> User | None:
        pager = Paginator(self.session, self.url, page_size=page_size)
        while pager.total is None or pager.seen < pager.total:
            result = pager.get_next_page()
            for u in result:
                user = User(
                    session=self.session,
                    url=urls.append_path(self.url, u["guid"]),
                    **u,
                )
                if filter(user):
                    return user
        return None

    def get(self, id: str) -> User:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        raw_user = response.json()
        return User(
            session=self.session,
            url=urls.append_path(self.url, raw_user["guid"]),
            **raw_user,
        )

    def create(self) -> User:
        raise NotImplementedError()

    def update(self) -> User:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()

    def count(self) -> int:
        response: requests.Response = self.session.get(
            self.url, params={"page_size": 1}
        )
        print(response.json())
        result: dict = response.json()
        return result["total"]
