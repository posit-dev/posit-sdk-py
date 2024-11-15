"""Permission resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, overload

from requests.sessions import Session as Session

from .resources import Resource, ResourceParameters, Resources

if TYPE_CHECKING:
    from .groups import Group
    from .users import User


class Permission(Resource):
    def destroy(self) -> None:
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

    def destroy(self, *permissions: str | Group | User | Permission) -> list[Permission]:
        """Delete permissions.

        Removes all provided permissions from the content item's permissions.

        Parameters
        ----------
        *permissions : str | Group | User | Permission
            The content item permissions to remove. If a `str` is received, it is compared agains
            the Permissions' `principal_gruid`. If a `Group`, `User`, or `Permission` is received,
            the `guid` is used and compared against the Permissions' `principal_guid`. If a
            `Permission` is received, the `principal_guid` is used.

        Returns
        -------
        list[Permission]
            The deleted permissions.

        Examples
        --------
        ```python
        from posit import connect

        #### User-defined inputs ####
        # 1. specify the guid for the content item
        content_guid = "CONTENT_GUID_HERE"
        # 2. specify either the principal_guid or group name prefix
        principal_guid = "USER_OR_GROUP_GUID_HERE"
        group_name_prefix = "GROUP_NAME_PREFIX_HERE"
        ############################

        client = connect.Client()

        # Remove a single permission by principal_guid
        client.content.get(content_guid).permissions.delete(principal_guid)

        # Remove by user (if principal_guid is a user)
        user = client.users.get(principal_guid)
        client.content.get(content_guid).permissions.delete(user)

        # Remove by group (if principal_guid is a group)
        group = client.groups.get(principal_guid)
        client.content.get(content_guid).permissions.destroy(group)

        # Remove all groups with a matching prefix name
        groups = client.groups.find(prefix=group_name_prefix)
        client.content.get(content_guid).permissions.destroy(*groups)

        # Confirm new permissions
        client.content.get(content_guid).permissions.find()
        ```
        """
        from .groups import Group
        from .users import User

        principal_guids: set[str] = set()

        for arg in permissions:
            if isinstance(arg, str):
                principal_guid = arg
            elif isinstance(arg, Group):
                principal_guid: str = arg["guid"]
            elif isinstance(arg, User):
                principal_guid: str = arg["guid"]
            elif isinstance(arg, Permission):
                principal_guid: str = arg["principal_guid"]
            else:
                raise TypeError(
                    f"destroy() expected argument type 'str', 'Group', 'Permission' or 'User', but got '{type(arg).__name__}'",
                )
            principal_guids.add(principal_guid)

        destroyed_permissions: list[Permission] = []
        for permission in self.find():
            if permission["principal_guid"] in principal_guids:
                permission.destroy()
                destroyed_permissions.append(permission)

        return destroyed_permissions
