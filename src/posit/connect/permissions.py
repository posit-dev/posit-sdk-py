"""Permission resources."""

from __future__ import annotations

from typing import List, overload

from requests.sessions import Session as Session

from . import urls

from .config import Config
from .resources import Resource, Resources


class Permission(Resource):
    @property
    def id(self) -> str:
        return self.get("id")  # type: ignore

    @property
    def content_guid(self) -> str:
        return self.get("content_guid")  # type: ignore

    @property
    def principal_guid(self) -> str:
        return self.get("principal_guid")  # type: ignore

    @property
    def principal_type(self) -> str:
        return self.get("principal_type")  # type: ignore

    @property
    def role(self) -> str:
        return self.get("role")  # type: ignore

    def delete(self) -> None:
        """Delete the permission."""
        path = f"v1/content/{self.content_guid}/permissions/{self.id}"
        url = urls.append(self.config.url, path)
        self.session.delete(url)

    @overload
    def update(self, role: str) -> None:
        """Update the permission.

        Parameters
        ----------
        role : str
            The principal role.
        """
        ...

    @overload
    def update(self, *args, **kwargs) -> None:
        """Update the permission."""
        ...

    def update(self, *args, **kwargs) -> None:
        """Update the permission."""
        body = {
            "principal_guid": self.principal_guid,
            "principal_type": self.principal_type,
            "role": self.role,
        }
        body.update(*args, **kwargs)
        path = f"v1/content/{self.content_guid}/permissions/{self.id}"
        url = urls.append(self.config.url, path)
        response = self.session.put(
            url,
            json=body,
        )
        super().update(**response.json())


class Permissions(Resources):
    def __init__(
        self, config: Config, session: Session, content_guid: str
    ) -> None:
        super().__init__(config, session)
        self.content_guid = content_guid

    def count(self) -> int:
        """Count the number of permissions.

        Returns
        -------
        int
        """
        return len(self.find())

    @overload
    def create(
        self, principal_guid: str, principal_type: str, role: str
    ) -> Permission:
        """Create a permission.

        Parameters
        ----------
        principal_guid : str
        principal_type : str
        role : str

        Returns
        -------
        Permission
        """
        ...

    @overload
    def create(self, *args, **kwargs) -> Permission:
        """Create a permission.

        Returns
        -------
        Permission
        """
        ...

    def create(self, *args, **kwargs) -> Permission:
        """Create a permission.

        Returns
        -------
        Permission
        """
        ...
        body = dict(*args, **kwargs)
        path = f"v1/content/{self.content_guid}/permissions"
        url = urls.append(self.config.url, path)
        response = self.session.post(url, json=body)
        return Permission(self.config, self.session, **response.json())

    def find(self, *args, **kwargs) -> List[Permission]:
        """Find permissions.

        Returns
        -------
        List[Permission]
        """
        body = dict(*args, **kwargs)
        path = f"v1/content/{self.content_guid}/permissions"
        url = urls.append(self.config.url, path)
        response = self.session.get(url, json=body)
        results = response.json()
        return [
            Permission(self.config, self.session, **result)
            for result in results
        ]

    def find_one(self, *args, **kwargs) -> Permission | None:
        """Find a permission.

        Returns
        -------
        Permission | None
        """
        permissions = self.find(*args, **kwargs)
        return next(iter(permissions), None)

    def get(self, id: str) -> Permission:
        """Get a permission.

        Parameters
        ----------
        id : str
            The permission id.

        Returns
        -------
        Permission
        """
        path = f"v1/content/{self.content_guid}/permissions/{id}"
        url = urls.append(self.config.url, path)
        response = self.session.get(url)
        return Permission(self.config, self.session, **response.json())
