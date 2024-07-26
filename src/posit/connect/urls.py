from __future__ import annotations

import posixpath

from urllib.parse import urlsplit, urlunsplit


class Url(str):
    def __new__(cls, value):
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        return super(Url, cls).__new__(cls, _create(value))

    def __init__(self, value):
        super(Url, self).__init__()

    def __add__(self, path: str):
        return self.append(path)

    def append(self, path: str) -> Url:
        return Url(_append(self, path))


def _create(url: str) -> str:
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
    if "/__api__" not in url:
        url = _append(url, "__api__")

    return url


def _append(url: str, path: str) -> str:
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
    >>> url + "path"
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
