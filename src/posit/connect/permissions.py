"""Permission resources."""

from __future__ import annotations

from typing import List, overload

from requests.sessions import Session as Session

from .resources import Resource, ResourceParameters, Resources


class Permission(Resource):
    def delete(self) -> None:
        """Delete the permission."""
        path = f"v1/content/{self['content_guid']}/permissions/{self['id']}"
        url = self.params.url + path
        self.params.session.delete(url)

    @overload
    def update(self, *args, role: str, **kwargs) -> None:
        """Update the permission.

        Parameters
        ----------
        role : str
            The principal role.
        """

    @overload
    def update(self, *args, **kwargs) -> None:
        """Update the permission."""

    def update(self, *args, **kwargs) -> None:
        """Update the permission."""
        body = {
            "principal_guid": self.get("principal_guid"),
            "principal_type": self.get("principal_type"),
            "role": self.get("role"),
        }
        body.update(dict(*args))
        body.update(**kwargs)
        path = f"v1/content/{self['content_guid']}/permissions/{self['id']}"
        url = self.params.url + path
        response = self.params.session.put(
            url,
            json=body,
        )
        super().update(**response.json())


class Permissions(Resources):
    def __init__(self, params: ResourceParameters, content_guid: str) -> None:
        super().__init__(params)
        self.content_guid = content_guid

    def count(self) -> int:
        """Count the number of permissions.

        Returns
        -------
        int
        """
        return len(self.find())

    @overload
    def create(self, *, principal_guid: str, principal_type: str, role: str) -> Permission:
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

    @overload
    def create(self, **kwargs) -> Permission:
        """Create a permission.

        Returns
        -------
        Permission
        """

    def create(self, **kwargs) -> Permission:
        """Create a permission.

        Returns
        -------
        Permission
        """
        path = f"v1/content/{self.content_guid}/permissions"
        url = self.params.url + path
        response = self.params.session.post(url, json=kwargs)
        return Permission(params=self.params, **response.json())

    def find(self, **kwargs) -> List[Permission]:
        """Find permissions.

        Returns
        -------
        List[Permission]
        """
        path = f"v1/content/{self.content_guid}/permissions"
        url = self.params.url + path
        response = self.params.session.get(url, json=kwargs)
        results = response.json()
        return [Permission(self.params, **result) for result in results]

    def find_one(self, **kwargs) -> Permission | None:
        """Find a permission.

        Returns
        -------
        Permission | None
        """
        permissions = self.find(**kwargs)
        return next(iter(permissions), None)

    def get(self, uid: str) -> Permission:
        """Get a permission.

        Parameters
        ----------
        uid : str
            The permission id.

        Returns
        -------
        Permission
        """
        path = f"v1/content/{self.content_guid}/permissions/{uid}"
        url = self.params.url + path
        response = self.params.session.get(url)
        return Permission(self.params, **response.json())
