"""Group resources."""

from __future__ import annotations

from typing import List, overload

from ._active import ActiveDict
from ._api_call import ApiCallMixin
from ._types_context import ContextP
from .context import Context
from .paginator import Paginator


class GroupContext(Context):
    group_guid: str

    def __init__(self, ctx: Context, /, *, group_guid: str):
        super().__init__(ctx.session, ctx.url)
        self.group_guid = group_guid


class Group(ActiveDict[GroupContext]):
    """Group resource."""

    def __init__(self, ctx: Context, /, *, guid: str, **kwargs):
        assert isinstance(guid, str), "guid must be a string"
        assert guid, "guid must not be empty"

        group_ctx = GroupContext(ctx, group_guid=guid)
        path = f"v1/groups/{guid}"
        get_data = len(kwargs) == 0
        super().__init__(group_ctx, path, get_data, guid=guid, **kwargs)

    def delete(self) -> None:
        """Delete the group."""
        self._delete_api()


class Groups(ApiCallMixin, ContextP[Context]):
    """Groups resource."""

    def __init__(self, ctx: Context):
        super().__init__()
        self._ctx = ctx
        self._path = "v1/groups"

    @overload
    def create(self, *, name: str, unique_id: str | None) -> Group:
        """Create a group.

        Parameters
        ----------
        name: str
        unique_id: str | None

        Returns
        -------
        Group
        """

    @overload
    def create(self, **kwargs) -> Group:
        """Create a group.

        Returns
        -------
        Group
        """

    def create(self, **kwargs) -> Group:
        """Create a group.

        Parameters
        ----------
        name: str
        unique_id: str | None

        Returns
        -------
        Group
        """
        result = self._post_api(json=kwargs)
        assert result is not None, "Group creation failed"
        return Group(self._ctx, **result)

    @overload
    def find(
        self,
        *,
        prefix: str = ...,
    ) -> List[Group]: ...

    @overload
    def find(self, **kwargs) -> List[Group]: ...

    def find(self, **kwargs):
        """Find groups.

        Parameters
        ----------
        prefix: str
            Filter by group name prefix. Casing is ignored.

        Returns
        -------
        List[Group]
        """
        url = self._ctx.url + self._path
        paginator = Paginator(self._ctx.session, url, params=kwargs)
        results = paginator.fetch_results()
        return [
            Group(
                self._ctx,
                **result,
            )
            for result in results
        ]

    @overload
    def find_one(
        self,
        *,
        prefix: str = ...,
    ) -> Group | None: ...

    @overload
    def find_one(self, **kwargs) -> Group | None: ...

    def find_one(self, **kwargs) -> Group | None:
        """Find one group.

        Parameters
        ----------
        prefix: str
            Filter by group name prefix. Casing is ignored.

        Returns
        -------
        Group | None
        """
        url = self._ctx.url + self._path
        paginator = Paginator(self._ctx.session, url, params=kwargs)
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        groups = (
            Group(
                self._ctx,
                **result,
            )
            for result in results
        )
        return next(groups, None)

    def get(self, guid: str) -> Group:
        """Get group.

        Parameters
        ----------
        guid : str

        Returns
        -------
        Group
        """
        return Group(
            self._ctx,
            guid=guid,
        )

    def count(self) -> int:
        """Count the number of groups.

        Returns
        -------
        int
        """
        result = self._get_api(params={"page_size": 1})
        assert result is not None, "Group count failed"
        assert "total" in result, "`'total'` key not found in Group response"
        return result["total"]
