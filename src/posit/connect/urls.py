from __future__ import annotations

import posixpath

from urllib.parse import urlsplit, urlunsplit


def append_path(url: str, path: str) -> str:
    """
    Appends a path to the end of a URL.

    Args:
        url (str): The URL to append the path to.
        path (str): The path to append to the URL.

    Returns:
        str: The modified URL with the appended path.

    Raises:
        ValueError: If the URL does not specify a scheme, is not absolute, or does not end with "/__api__".

    Example:
        >>> append_path("http://example.com", "api")
        'http://example.com/__api__/api'
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

    if not (split.path and split.path.endswith("/__api__")):
        raise ValueError(
            f"url must end with path __api__ (e.g., http://example.com/__api__): {url}"
        )

    joined_path = posixpath.join(split.path, path.lstrip("/"))

    # See https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlunsplit
    return urlunsplit((split.scheme, split.netloc, joined_path, split.query, None))
