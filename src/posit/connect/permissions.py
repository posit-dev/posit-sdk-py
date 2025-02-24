"""Permission resources."""

from __future__ import annotations

from requests.sessions import Session as Session
from typing_extensions import TYPE_CHECKING, List, Optional, overload

from .resources import BaseResource, Resources

if TYPE_CHECKING:
    from .context import Context
    from .groups import Group
    from .users import User


class Permission(BaseResource):
    def destroy(self) -> None:
        """Destroy the permission."""
        path = f"v1/content/{self['content_guid']}/permissions/{self['id']}"
        self._ctx.client.delete(path)

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
        response = self._ctx.client.put(path, json=body)
        super().update(**response.json())


class Permissions(Resources):
    def __init__(self, ctx: Context, content_guid: str) -> None:
        super().__init__(ctx)
        self.content_guid = content_guid

    def count(self) -> int:
        """Count the number of permissions.

        Returns
        -------
        int
        """
        return len(self.find())

    @overload
    def create(self, /, *, principal_guid: str, principal_type: str, role: str) -> Permission: ...

    @overload
    def create(self, principal: User | Group, /, *, role: str) -> Permission: ...

    def create(
        self,
        principal: Optional[User | Group] = None,
        /,
        **kwargs,
    ) -> Permission:
        """Create a permission.

        Parameters
        ----------
        principal : User | Group
            The principal user or group to add.
        role : str
            The principal role. Currently only `"viewer"` and `"owner"` are supported.
        principal_guid : str
            User guid or Group guid.
        principal_type : str
            The principal type. Either `"user"` or `"group"`.
        role : str
            The principal role. Currently only `"viewer"` and `"owner"` are supported

        Returns
        -------
        Permission
            The created permission.

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
        group = groups[0]
        user = client.users.get("USER_GUID_HERE")
        users_and_groups = [user, *groups]

        # Add a group permission
        content_item.permissions.create(group, role=role)
        # Add a user permission
        content_item.permissions.create(user, role=role)

        # Add many group and user permissions with the same role
        for principal in users_and_groups:
            content_item.permissions.create(principal, role=role)

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
        if principal is not None:
            # Avoid circular imports
            from .groups import Group
            from .users import User

            if isinstance(principal, User):
                principal_type = "user"
            elif isinstance(principal, Group):
                principal_type = "group"
            else:
                raise TypeError(f"Invalid argument type: {type(principal).__name__}")

            if "principal_guid" in kwargs:
                raise ValueError("'principal_guid' can not be defined with `principal` present.")
            if "principal_type" in kwargs:
                raise ValueError("'principal_guid' can not be defined with `principal` present.")

            # Set the corresponding kwargs
            kwargs["principal_guid"] = principal["guid"]
            kwargs["principal_type"] = principal_type

        path = f"v1/content/{self.content_guid}/permissions"
        response = self._ctx.client.post(path, json=kwargs)
        return Permission(self._ctx, **response.json())

    def find(self, **kwargs) -> List[Permission]:
        """Find permissions.

        Returns
        -------
        List[Permission]
        """
        path = f"v1/content/{self.content_guid}/permissions"
        response = self._ctx.client.get(path)
        kwargs_items = kwargs.items()
        results = response.json()
        if len(kwargs_items) > 0:
            results = [
                result
                for result in results
                if isinstance(result, dict) and (result.items() >= kwargs_items)
            ]
        return [Permission(self._ctx, **result) for result in results]

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
        response = self._ctx.client.get(path)
        return Permission(self._ctx, **response.json())

    def destroy(self, permission: str | Group | User | Permission, /) -> None:
        """Remove supplied content item permission.

        Removes provided permission from the content item's permissions.

        Parameters
        ----------
        permission : str | Group | User | Permission
            The content item permission to remove. If a `str` is received, it is compared against
            the `Permissions`'s `principal_guid`. If a `Group` or `User` is received, the associated
            `Permission` will be removed.

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
        content_item = client.content.get(content_guid)

        # Remove a single permission by principal_guid
        content_item.permissions.destroy(principal_guid)

        # Remove by user (if principal_guid is a user)
        user = client.users.get(principal_guid)
        content_item.permissions.destroy(user)

        # Remove by group (if principal_guid is a group)
        group = client.groups.get(principal_guid)
        content_item.permissions.destroy(group)

        # Remove all groups with a matching prefix name
        groups = client.groups.find(prefix=group_name_prefix)
        for group in groups:
            content_item.permissions.destroy(group)

        # Confirm new permissions
        content_item.permissions.find()
        ```
        """
        from .groups import Group
        from .users import User

        if isinstance(permission, str):
            permission_obj = self.get(permission)
        elif isinstance(permission, (Group, User)):
            principal_guid: str = permission["guid"]
            permission_obj = self.find_one(
                principal_guid=principal_guid,
            )
            if permission_obj is None:
                raise ValueError(f"Permission with principal_guid '{principal_guid}' not found.")
        elif isinstance(permission, Permission):
            permission_obj = permission
        else:
            raise TypeError(
                f"destroy() expected `permission=` to have type `str | User | Group | Permission`. Received `{permission}` of type `{type(permission)}`.",
            )

        permission_obj.destroy()
