from __future__ import annotations

import posixpath
from urllib.parse import urlsplit, urlunsplit


class Url(str):
    """URL representation for Connect.

    An opinionated URL representation of a Connect URL. Maintains various
    conventions:
        - It begins with a scheme.
        - It is absolute.
        - It contains '__api__'.

    Supports Python builtin __add__ for append.

    Methods
    -------
    append(path: str)
        Append a path to the URL.

    Examples
    --------
    >>> url = Url("http://connect.example.com/")
    http://connect.example.com/__api__
    >>> url + "endpoint"
    http://connect.example.com/__api__/endpoint

    Append works with string-like objects (e.g., objects that support casting to string)
    >>> url = Url("http://connect.example.com/__api__/endpoint")
    http://connect.example.com/__api__/endpoint
    >>> url + 1
    http://connect.example.com/__api__/endpoint/1
    """

    def __new__(cls, value: str):
        url = _create(value)
        return super(Url, cls).__new__(cls, url)

    def __add__(self, path: str):
        return self.append(path)

    def append(self, path: str) -> Url:
        return Url(_append(self, path))


def _create(url: str) -> str:
    """Create a URL.

    Asserts that the URL is a proper Posit Connect endpoint. The path '__api__' is appended to the URL if it is missing.

    Parameters
    ----------
    url : str
        The original URL.

    Returns
    -------
    Url
        The validated and formatted URL.

    Raises
    ------
    ValueError
        The Url is missing a scheme.
    ValueError
        The Url is missing a network location (i.e., a domain name).

    Examples
    --------
    >>> _create("http://example.com")
    http://example.com/__api__

    >>> _create("http://example.com/__api__")
    http://example.com/__api__
    """
    split = urlsplit(url, allow_fragments=False)
    if not split.scheme:
        raise ValueError(f"URL must specify a scheme (e.g., http://example.com/__api__): {url}")
    if not split.netloc:
        raise ValueError(f"URL must be absolute (e.g., http://example.com/__api__): {url}")

    url = url.rstrip("/")
    if "/__api__" not in url:
        url = _append(url, "__api__")

    return url


def _append(url: str, path) -> str:
    """Append a path to a Url.

    Parameters
    ----------
    url : str
        A valid URL.
    path : str
        A valid path.

    Returns
    -------
    Url
        The original Url with the path appended to the end.

    Examples
    --------
    >>> url = _create("http://example.com/__api__")
    >>> _append(url, "path")
    http://example.com/__api__/path
    """
    path = str(path).strip("/")
    split = urlsplit(url, allow_fragments=False)
    new_path = posixpath.join(split.path, path)
    return urlunsplit((split.scheme, split.netloc, new_path, split.query, None))
