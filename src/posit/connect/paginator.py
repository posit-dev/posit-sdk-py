from collections.abc import Iterable
from typing import Iterator, List

import requests


class Paginator(Iterable):
    """
    Paginator class for iterating over paginated API responses.

    Args:
        session (requests.Session): The requests session object to use for making API requests.
        url (str): The URL of the API endpoint to fetch paginated results from.
        page_size (int): The number of items to fetch per page.

    Attributes:
        elements (List[dict]): The list of fetched elements.
        exhausted (bool): Indicates whether all pages have been fetched.
        index (int): The current index of the elements list.
        page_size (int): The number of items to fetch per page.
        session (requests.Session): The requests session object to use for making API requests.
        url (str): The URL of the API endpoint to fetch paginated results from.
    """

    def __init__(self, session: requests.Session, url: str, *, page_size: int) -> None:
        self.elements: List[dict] = []
        self.exhausted = False
        self.index = 0
        self.page_size = page_size
        self.session = session
        self.url = url

    def __iter__(self) -> Iterator[dict]:
        """
        Returns an iterator object for the Paginator class.

        Returns:
            Iterator[dict]: An iterator object that iterates over the items in the Paginator.
        """
        self.index = 0
        return self

    def __len__(self) -> int:
        """
        Returns the total number of items in the paginator.

        Returns:
            int: The total number of items in the paginator.
        """
        # Define query parameters for pagination.
        params = {"page_number": 1, "page_size": 1}
        # Send a GET request to the endpoint with the specified parameters.
        response = self.session.get(self.url, params=params)
        # Convert response to dict
        as_dict = response.json()
        # Return total as int
        return int(as_dict["total"])

    def __next__(self) -> dict:
        """
        Returns the next element in the paginator.

        Raises:
            StopIteration: If there are no more elements to iterate over.

        Returns:
            dict: The next element in the paginator.
        """
        if self.index >= len(self.elements):
            if self.exhausted:
                raise StopIteration

            page = int(self.index / self.page_size) + 1
            results, self.exhausted = self.fetch(page)
            if not results:
                raise StopIteration

            self.elements += results

        v = self.elements[self.index]
        self.index += 1
        return v

    def fetch(self, page: int) -> tuple[Iterator[dict] | None, bool]:
        """
        Fetches a specific page of results from the API.

        Args:
            page (int): The page number to fetch. Must be greater than 0.

        Returns:
            tuple[Iterator[dict] | None, bool]: A tuple containing the fetched results and a boolean indicating
            whether there are more pages to fetch.

        Raises:
            ValueError: If the page number is not greater than 0.
        """
        # Check if page is greater than 0
        if not (page > 0):
            raise ValueError(f"page must be greater than 0, got {page}")
        # Define query parameters for pagination.
        params = {"page_number": page, "page_size": self.page_size}
        # Send a GET request to the endpoint with the specified parameters.
        response = self.session.get(self.url, params=params)
        # Convert response to dict
        as_dict: dict = dict(response.json())
        # Parse the JSON response and extract the results.
        results = as_dict["results"]
        # Mark exhausted if the result size is less than the maximum page size.
        exhausted = len(results) < self.page_size
        return (results, exhausted)
