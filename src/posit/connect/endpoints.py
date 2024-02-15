import os
import requests

_MAX_PAGE_SIZE = 500


def get_users(
    endpoint: str,
    session: requests.Session,
    /,
    page_number: int,
    *,
    page_size: int = 500,
):
    """
    Fetches the current page of users.

    Returns:
        List[User]: A list of User objects representing the fetched users.
    """
    # Construct the endpoint URL.
    endpoint = os.path.join(endpoint, "v1/users")
    # Redefine the page number using 1-based indexing.
    page_number = page_number + 1
    # Define query parameters for pagination.
    params = {"page_number": page_number, "page_size": page_size}
    # Send a GET request to the endpoint with the specified parameters.
    response = session.get(endpoint, params=params)
    # Convert response to dict
    json = response.json()
    # Parse the JSON response and extract the results.
    results = json["results"]
    # Mark exhausted if the result size is less than the maximum page size.
    exhausted = len(results) < page_size
    # Create User objects from the results and return them as a list.
    return (results, exhausted)
