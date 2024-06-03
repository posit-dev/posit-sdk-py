from __future__ import annotations

import posixpath

from urllib.parse import urlsplit, urlunsplit

Url = str


def create(url: str) -> Url:
    """Create a Url.

    Asserts that the Url is a proper Posit Connect endpoint. The path '__api__' is appended to the Url if it isn't already present.

    Parameters
    ----------
    url : str
        The original Url.

    Returns
    -------
    Url
        The validated and formatted Url.

    Raises
    ------
    ValueError
        The Url is missing a scheme.
    ValueError
        The Url is missing a network location (i.e., a domain name).

    Examples
    --------
    >>> urls.create("http://example.com")
    http://example.com/__api__

    >>> urls.create("http://example.com/__api__")
    http://example.com/__api__

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

    url = url.rstrip("/")
    if not url.endswith("__api__"):
        url = append(url, "__api__")

    return url


def append(url: Url, path: str) -> Url:
    """Append a path to a Url.

    Parameters
    ----------
    url : Url
        A valid Url.
    path : str
        A valid Url path.

    Returns
    -------
    Url
        The original Url with the path appended to the end.

    Examples
    --------
    >>> url = urls.create("http://example.com/__api__")
    >>> urls.append(url, "path")
    http://example.com/__api__/path
    """
    # Removes leading '/' from path to avoid double slashes.
    path = path.lstrip("/")
    # Removes trailing '/' from path to avoid double slashes.
    path = path.rstrip("/")
    # See https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlsplit
    split = urlsplit(url, allow_fragments=False)
    # Append the path to unmodified Url path.
    path = posixpath.join(split.path, path)
    # See https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlunsplit
    return urlunsplit((split.scheme, split.netloc, path, split.query, None))
