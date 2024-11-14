"""Permission resources."""

from __future__ import annotations

from typing import List, overload

from ._active import ActiveDict
from ._types_content_item import ContentItemContext
from ._types_context import ContextP


class PermissionContext(ContentItemContext):
    permission_id: str

    def __init__(self, ctx: ContentItemContext, /, *, permission_id: str) -> None:
        super().__init__(ctx, content_guid=ctx.content_guid)
        self.permission_id = permission_id


class Permission(ActiveDict[PermissionContext]):
    @classmethod
    def _api_path(cls, content_guid: str, permission_id: str) -> str:
        return f"v1/content/{content_guid}/permissions/{permission_id}"

    def __init__(self, ctx: ContentItemContext, /, **kwargs) -> None:
        permission_id = kwargs.get("id")
        assert isinstance(
            permission_id, str
        ), f"Permission 'id' must be a string. Got: {permission_id}"
        assert permission_id, "Permission 'id' must not be an empty string."

        permission_ctx = PermissionContext(
            ctx,
            permission_id=permission_id,
        )
        path = self._api_path(permission_ctx.content_guid, permission_ctx.permission_id)
        get_data = len(kwargs) == 1  # `id` is required

        super().__init__(permission_ctx, path, get_data, **kwargs)

    def delete(self) -> None:
        """Delete the permission."""
        self._delete_api()

    @overload
    def update(self, *args, role: str, **kwargs) -> Permission:
        """Update the permission.

        Parameters
        ----------
        role : str
            The principal role.
        """

    @overload
    def update(self, *args, **kwargs) -> Permission:
        """Update the permission."""

    def update(self, *args, **kwargs) -> Permission:
        """Update the permission."""
        body = {
            "principal_guid": self.get("principal_guid"),
            "principal_type": self.get("principal_type"),
            "role": self.get("role"),
        }
        body.update(dict(*args))
        body.update(**kwargs)
        result = self._put_api(json=body)
        return Permission(self._ctx, **result)


class Permissions(ContextP[ContentItemContext]):
    def __init__(self, ctx: ContentItemContext) -> None:
        super().__init__()
        self._ctx = ctx

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
        path = f"v1/content/{self._ctx.content_guid}/permissions"
        url = self._ctx.url + path
        response = self._ctx.session.post(url, json=kwargs)
        return Permission(self._ctx, **response.json())

    def find(self, **kwargs) -> List[Permission]:
        """Find permissions.

        Returns
        -------
        List[Permission]
        """
        path = f"v1/content/{self._ctx.content_guid}/permissions"
        url = self._ctx.url + path
        response = self._ctx.session.get(url, json=kwargs)
        results = response.json()
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
        return Permission(self._ctx, id=uid)
