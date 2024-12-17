from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import TYPE_CHECKING, Generator, List

if TYPE_CHECKING:
    from .context import Context

# The maximum page size supported by the API.
_MAX_PAGE_SIZE = 500


@dataclass
class Page:
    """
    Represents a page of results returned by the paginator.

    Attributes
    ----------
        current_page (int): The current page number.
        total (int): The total number of results.
        results (List[dict]): The list of results on the current page.
    """

    current_page: int
    total: int
    results: List[dict]


class Paginator:
    """
    A class for paginating through API results.

    Args:
        session (requests.Session): The session object to use for making API requests.
        url (str): The URL of the paginated API endpoint.

    Attributes
    ----------
        session (requests.Session): The session object to use for making API requests.
        url (str): The URL of the paginated API endpoint.
    """

    def __init__(
        self,
        ctx: Context,
        path: str,
        params: dict | None = None,
    ) -> None:
        if params is None:
            params = {}
        self._ctx = ctx
        self._path = path
        self._params = params

    def fetch_results(self) -> List[dict]:
        """
        Fetches and returns all the results from the paginated API endpoint.

        Returns
        -------
            A list of dictionaries representing the fetched results.
        """
        results = []
        for page in self.fetch_pages():
            results.extend(page.results)
        return results

    def fetch_pages(self) -> Generator[Page, None, None]:
        """
        Fetches pages of results from the API.

        Yields
        ------
            Page: A page of results from the API.
        """
        count = 0
        page_number = 1
        while True:
            page = self.fetch_page(page_number)
            page_number += 1
            if len(page.results) > 0:
                yield page
            else:
                # stop if the result set is empty
                return

            count += len(page.results)
            # Check if the local count has reached the total threshold.
            # It is possible for count to exceed total if the total changes
            # during execution of this loop.
            # It is also possible for the total to change between iterations.
            if count >= page.total:
                break

    def fetch_page(self, page_number: int) -> Page:
        """
        Fetches a specific page of data from the API.

        Args:
            page_number (int): The page number to fetch.

        Returns
        -------
            Page: The fetched page object.

        """
        params = {
            **self._params,
            "page_number": page_number,
            "page_size": _MAX_PAGE_SIZE,
        }
        response = self._ctx.client.get(self._path, params=params)
        return Page(**response.json())
