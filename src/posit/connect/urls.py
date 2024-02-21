from __future__ import annotations

import posixpath

from urllib.parse import urlsplit, urlunsplit


def server_to_api_url(url: str) -> str:
    """
    Fixes the given URL by appending '__api__' if it doesn't already end with it.

    Args:
        url (str): The URL to fix.

    Returns:
        str: The fixed URL.
    """
    url = url.rstrip("/")
    if not url.endswith("__api__"):
        return append_path(url, "__api__")
    return url


def validate(url: str) -> None:
    """
    Check if the given URL is valid.

    Args:
        url (str): The URL to be validated.

    Returns:
        bool: True if the URL is valid, False otherwise.

    Raises:
        ValueError: If the URL is missing a scheme or is not absolute.
    """
    split = urlsplit(url, allow_fragments=False)
    if not split.scheme:
        raise ValueError(
            f"url must specify a scheme (e.g., http://example.com/__api__): {url}"
        )

    if not split.netloc:
        raise ValueError(
            f"url must be absolute (e.g., http://example.com/__api__): {url}"
        )


def append_path(url: str, path: str) -> str:
    """
    Appends a path to a URL.

    Args:
        url (str): The original URL.
        path (str): The path to append.

    Returns:
        str: The modified URL with the appended path.
    """
    # See https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlsplit
    split = urlsplit(url, allow_fragments=False)
    # Removes leading '/' from path to avoid double slashes.
    path = path.lstrip("/")
    # Prepend the path with the existing URL path.
    path = posixpath.join(split.path, path)
    # See https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlunsplit
    return urlunsplit((split.scheme, split.netloc, path, split.query, None))
