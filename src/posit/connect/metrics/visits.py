from __future__ import annotations

from typing_extensions import List, overload

from ..cursors import CursorPaginator
from ..resources import BaseResource, Resources


class VisitEvent(BaseResource):
    @property
    def content_guid(self) -> str:
        """The associated unique content identifier.

        Returns
        -------
        str
        """
        return self["content_guid"]

    @property
    def user_guid(self) -> str:
        """The associated unique user identifier.

        Returns
        -------
        str
        """
        return self["user_guid"]

    @property
    def rendering_id(self) -> int | None:
        """The render id associated with the visit.

        Returns
        -------
        int | None
            The render id, or None if the associated content type is static.
        """
        return self["rendering_id"]

    @property
    def bundle_id(self) -> int:
        """The bundle id associated with the visit.

        Returns
        -------
        int
        """
        return self["bundle_id"]

    @property
    def variant_key(self) -> str | None:
        """The variant key associated with the visit.

        Returns
        -------
        str | None
            The variant key, or None if the associated content type is static.
        """
        return self.get("variant_key")

    @property
    def time(self) -> str:
        """The visit timestamp.

        Returns
        -------
        str
        """
        return self["time"]

    @property
    def data_version(self) -> int:
        """The data version.

        Returns
        -------
        int
        """
        return self["data_version"]

    @property
    def path(self) -> str:
        """The path requested by the user.

        Returns
        -------
        str
        """
        return self["path"]


class Visits(Resources):
    @overload
    def find(
        self,
        *,
        content_guid: str = ...,
        min_data_version: int = ...,
        start: str = ...,
        end: str = ...,
    ) -> List[VisitEvent]:
        """Find visits.

        Parameters
        ----------
        content_guid : str, optional
            Filter by an associated unique content identifer, by default ...
        min_data_version : int, optional
            Filter by a minimum data version, by default ...
        start : str, optional
            Filter by the start time, by default ...
        end : str, optional
            Filter by the end time, by default ...

        Returns
        -------
        List[Visit]
        """

    @overload
    def find(self, **kwargs) -> List[VisitEvent]:
        """Find visits.

        Returns
        -------
        List[Visit]
        """

    def find(self, **kwargs) -> List[VisitEvent]:
        """Find visits.

        Returns
        -------
        List[Visit]
        """
        params = rename_params(kwargs)

        path = "/v1/instrumentation/content/visits"
        paginator = CursorPaginator(self._ctx, path, params=params)
        results = paginator.fetch_results()
        return [
            VisitEvent(
                self._ctx,
                **result,
            )
            for result in results
        ]

    @overload
    def find_one(
        self,
        *,
        content_guid: str = ...,
        min_data_version: int = ...,
        start: str = ...,
        end: str = ...,
    ) -> VisitEvent | None:
        """Find a visit.

        Parameters
        ----------
        content_guid : str, optional
            Filter by an associated unique content identifer, by default ...
        min_data_version : int, optional
            Filter by a minimum data version, by default ...
        start : str, optional
            Filter by the start time, by default ...
        end : str, optional
            Filter by the end time, by default ...

        Returns
        -------
        Visit | None
        """

    @overload
    def find_one(self, **kwargs) -> VisitEvent | None:
        """Find a visit.

        Returns
        -------
        Visit | None
        """

    def find_one(self, **kwargs) -> VisitEvent | None:
        """Find a visit.

        Returns
        -------
        Visit | None
        """
        params = rename_params(kwargs)
        path = "/v1/instrumentation/content/visits"
        paginator = CursorPaginator(self._ctx, path, params=params)
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        visits = (
            VisitEvent(
                self._ctx,
                **result,
            )
            for result in results
        )
        return next(visits, None)


def rename_params(params: dict) -> dict:
    """Rename params from the internal to the external signature.

    The API accepts `from` as a querystring parameter. Since `from` is a reserved word in Python, the SDK uses the name `start` instead. The querystring parameter `to` takes the same form for consistency.

    Parameters
    ----------
    params : dict

    Returns
    -------
    dict
    """
    if "start" in params:
        params["from"] = params["start"]
        del params["start"]

    if "end" in params:
        params["to"] = params["end"]
        del params["end"]

    return params
