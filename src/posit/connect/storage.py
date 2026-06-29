"""Bundle storage resources.

These resources expose the admin-only bundle storage usage endpoints added in
Connect 2026.06.0:

- ``GET /v1/system/storage`` — server-wide bundle storage totals.
- ``GET /v1/content/storage`` — per-content bundle storage usage.
- ``GET /v1/content/{guid}/storage`` — bundle storage details for one content item.
"""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, List, Literal, Optional

from .context import ContextManager, requires
from .paginator import _MAX_PAGE_SIZE
from .resources import BaseResource

if TYPE_CHECKING:
    from .context import Context


class ServerStorage(BaseResource):
    """Aggregate bundle storage metrics for the Connect server.

    Attributes
    ----------
    bundles : dict
        Bundle storage metrics with the following keys:

        - ``bytes_total`` (int): Total bytes across all bundle archives with recorded sizes.
        - ``bytes_active`` (int): Bytes used by currently active (deployed) bundles.
        - ``bytes_inactive`` (int): Bytes used by inactive (historical) bundles.
        - ``count`` (int): Total number of bundles with recorded sizes.
        - ``content_count`` (int): Number of distinct content items with bundles.
    """


class ContentStorageItem(BaseResource):
    """Bundle storage metrics for a single content item.

    Attributes
    ----------
    content_guid : str
        The unique identifier of the content item.
    content_name : str
        The URL-safe name of the content item.
    content_title : str | None
        The human-friendly title of the content item, or ``None``.
    owner_guid : str | None
        The unique identifier of the content owner, or ``None``.
    owner_username : str | None
        The username of the content owner, or ``None``.
    app_mode : str
        The type of content (e.g., ``shiny``, ``rmd``, ``python-api``).
    bundles : dict
        Bundle storage metrics with ``count``, ``bytes_total``, ``bytes_active``, and
        ``bytes_inactive`` keys.
    """


class ContentStorageDetail(BaseResource):
    """Detailed bundle storage information for a content item.

    Attributes
    ----------
    content_guid : str
        The unique identifier of the content item.
    content_name : str
        The name of the content item.
    owner_guid : str | None
        The unique identifier of the content owner, or ``None``.
    owner_username : str | None
        The username of the content owner, or ``None``.
    bundle_count : int
        The number of bundles for this content item.
    bundle_bytes_total : int
        Total bytes across all bundles for this content.
    bundle_bytes_active : int
        Bytes used by the currently active (deployed) bundle.
    bundle_bytes_inactive : int
        Bytes used by inactive (historical) bundles.
    bundles : list of dict
        Per-bundle storage details, sorted by creation time (newest first). Each entry
        has ``id``, ``created_time``, ``size_bytes``, and ``is_active`` keys.
    """


class ContentStorage(ContextManager):
    """Bundle storage usage across all content items.

    This information is available only to administrators.
    """

    def __init__(self, ctx: Context, path: str) -> None:
        super().__init__()
        self._ctx: Context = ctx
        # v1/content/storage
        self._path: str = path

    @requires(version="2026.06.0")
    def find(
        self,
        *,
        sort: Optional[str] = None,
        order: Optional[Literal["asc", "desc"]] = None,
    ) -> List[ContentStorageItem]:
        """List bundle storage usage for every content item.

        Results are paginated by the server; this method fetches and returns all pages.

        This information is available only to administrators.

        Parameters
        ----------
        sort : str, optional
            The field to sort by.
        order : Literal['asc', 'desc'], optional
            The sort order.

        Returns
        -------
        List[ContentStorageItem]
            Bundle storage metrics for each content item.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client()

        items = client.content.storage.find()
        for item in items:
            print(item["content_name"], item["bundles"]["bytes_total"])
        ```
        """
        params = {}
        if sort is not None:
            params["sort"] = sort
        if order is not None:
            params["order"] = order

        results: List[ContentStorageItem] = []
        page_number = 1
        while True:
            response = self._ctx.client.get(
                self._path,
                params={**params, "page_number": page_number, "page_size": _MAX_PAGE_SIZE},
            )
            body = response.json()
            page_results = body["results"]
            results.extend(ContentStorageItem(self._ctx, **result) for result in page_results)

            if not page_results or page_number >= body["total_pages"]:
                break
            page_number += 1

        return results
