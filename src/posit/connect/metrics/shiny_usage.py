from __future__ import annotations

from typing_extensions import List, overload

from ..cursors import CursorPaginator
from ..resources import BaseResource, Resources


class ShinyUsageEvent(BaseResource):
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
    def started(self) -> str:
        """The started timestamp.

        Returns
        -------
        str
        """
        return self["started"]

    @property
    def ended(self) -> str:
        """The ended timestamp.

        Returns
        -------
        str
        """
        return self["ended"]

    @property
    def data_version(self) -> int:
        """The data version.

        Returns
        -------
        int
        """
        return self["data_version"]


class ShinyUsage(Resources):
    @overload
    def find(
        self,
        *,
        content_guid: str = ...,
        min_data_version: int = ...,
        start: str = ...,
        end: str = ...,
    ) -> List[ShinyUsageEvent]:
        """Find usage.

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
        List[ShinyUsageEvent]
        """

    @overload
    def find(self, **kwargs) -> List[ShinyUsageEvent]:
        """Find usage.

        Returns
        -------
        List[ShinyUsageEvent]
        """

    def find(self, **kwargs) -> List[ShinyUsageEvent]:
        """Find usage.

        Returns
        -------
        List[ShinyUsageEvent]
        """
        params = rename_params(kwargs)

        path = "/v1/instrumentation/shiny/usage"
        paginator = CursorPaginator(self._ctx, path, params=params)
        results = paginator.fetch_results()
        return [
            ShinyUsageEvent(
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
    ) -> ShinyUsageEvent | None:
        """Find a usage event.

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
        ShinyUsageEvent | None
        """

    @overload
    def find_one(self, **kwargs) -> ShinyUsageEvent | None:
        """Find a usage event.

        Returns
        -------
        ShinyUsageEvent | None
        """

    def find_one(self, **kwargs) -> ShinyUsageEvent | None:
        """Find a usage event.

        Returns
        -------
        ShinyUsageEvent | None
        """
        params = rename_params(kwargs)
        path = "/v1/instrumentation/shiny/usage"
        paginator = CursorPaginator(self._ctx, path, params=params)
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        visits = (
            ShinyUsageEvent(
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
