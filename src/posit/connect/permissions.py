"""Permission resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, overload

from requests.sessions import Session as Session

from .resources import Resource, ResourceParameters, Resources

if TYPE_CHECKING:
    from .groups import Group
    from .users import User


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
            User guid or Group guid.
        principal_type : str
            The principal type. Either `"user"` or `"group"`.
        role : str
            The principal role. Currently only `"viewer"` and `"owner"` are supported

        Returns
        -------
        Permission
        """

    @overload
    def create(self, *args: User | Group, role: str) -> list[Permission]:
        """Create a permission.

        Parameters
        ----------
        *args : User | Group
            The principal users or groups to add.
        role : str
            The principal role. Currently only `"viewer"` and `"owner"` are supported.

        Returns
        -------
        Permission

        Examples
        --------
        ```python
        from posit import connect

        client = connect.Client()
        content_item = client.content.get(content_guid)

        # New permission role
        role = "viewer"  # Or "owner"

        # Example groups and users
        groups = client.groups.find(prefix="GROUP_NAME_PREFIX_HERE")
        user = client.users.get("USER_GUID_HERE")
        users = [user]

        # Add many group and user permissions with the same role
        content_item.permissions.create(*groups, *users, role=role)

        # Add a group permission
        group = groups[0]
        content_item.permissions.create(group, role=role)
        # Add a user permission
        content_item.permissions.create(user, role=role)

        # Add a group permission manually
        content_item.permissions.create(
            principal_guid=group["guid"],
            principal_type="group",
            role=role,
        )
        # Add a user permission manually
        content_item.permissions.create(
            principal_guid=user["guid"],
            principal_type="user",
            role=role,
        )

        # Confirm new permissions
        content_item.permissions.find()
        ```
        """

    def create(self, *args: User | Group, **kwargs) -> Permission | list[Permission]:
        if len(args) > 0:
            # Avoid circular imports
            from .groups import Group
            from .users import User

            for arg in args:
                if not isinstance(arg, (User, Group)):
                    raise TypeError(f"Invalid argument type: {type(arg)}")
            if "principal_guid" in kwargs:
                raise ValueError("'principal_guid' can not be defined with `*args` present.")

            perms: list[Permission] = []
            for arg in args:
                if isinstance(arg, User):
                    principal_type = "user"
                elif isinstance(arg, Group):
                    principal_type = "group"
                else:
                    raise TypeError(f"Invalid argument type: {type(arg)}")

                perm = self.create(
                    principal_guid=arg["guid"],
                    principal_type=principal_type,
                    role=kwargs["role"],
                )
                perms.append(perm)
            return perms

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
