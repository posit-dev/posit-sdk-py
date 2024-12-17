from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import TYPE_CHECKING, Any, Generator, List

if TYPE_CHECKING:
    from .context import Context

# The maximum page size supported by the API.
_MAX_PAGE_SIZE = 500


@dataclass
class CursorPage:
    paging: dict
    results: List[dict]


class CursorPaginator:
    def __init__(
        self,
        ctx: Context,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> None:
        if params is None:
            params = {}

        self._ctx = ctx
        self._path = path
        self._params = params

    def fetch_results(self) -> List[dict]:
        """Fetch results.

        Collects all results from all pages.

        Returns
        -------
        List[dict]
            A coalesced list of all results.
        """
        results = []
        for page in self.fetch_pages():
            results.extend(page.results)
        return results

    def fetch_pages(self) -> Generator[CursorPage, None, None]:
        """Fetch pages.

        Yields
        ------
        Generator[Page, None, None]
        """
        next_page = None
        while True:
            page = self.fetch_page(next_page)
            yield page
            cursors: dict = page.paging.get("cursors", {})
            next_page = cursors.get("next")
            if not next_page:
                # stop if a next page is not defined
                return

    def fetch_page(self, next_page: str | None = None) -> CursorPage:
        """Fetch a page.

        Parameters
        ----------
        next : str | None, optional
            the next page identifier or None to fetch the first page, by default None

        Returns
        -------
        Page
        """
        params = {
            **self._params,
            "next": next_page,
            "limit": _MAX_PAGE_SIZE,
        }
        response = self._ctx.client.get(self._path, params=params)
        return CursorPage(**response.json())
