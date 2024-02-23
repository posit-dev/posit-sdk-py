from typing import List


# The maximum page size supported by the API.
_MAX_PAGE_SIZE = 500


class Paginator:
    """
    Utility for consuming Connect APIs that have pagination

    Usage:

        pager = Paginator(client.session, url)
        pager.get_all() # To return a list with results from all pages concatenated
        pager.get_next_page() # To step through one page at a time
    """

    def __init__(
        self, session, url, start_page: int = 1, page_size=_MAX_PAGE_SIZE
    ) -> None:
        self.session = session
        self.url = url
        self.page_number = start_page
        self.page_size = page_size
        # The API response will tell us how many total entries there are,
        # but we don't know yet.
        self.total = None
        # We also want to track how many results we've seen so far
        self.seen = 0

    def get_all(self) -> List[dict]:
        result = []
        while self.total is None or self.seen < self.total:
            result += self.get_next_page()
            self.page_number += 1
        return result

    def get_next_page(self) -> List[dict]:
        # Define query parameters for pagination.
        params = {"page_number": self.page_number, "page_size": self.page_size}
        # Send a GET request to the endpoint with the specified parameters.
        response = self.session.get(self.url, params=params).json()
        # On our first request, we won't have set the total yet, so do it
        if self.total is None:
            self.total = response["total"]
        results = response["results"]
        self.seen += len(results)
        return results
