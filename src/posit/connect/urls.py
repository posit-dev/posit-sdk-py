from __future__ import annotations

import posixpath
from urllib.parse import urlsplit, urlunsplit


class Url(str):
    def __new__(cls, value):
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        return super(Url, cls).__new__(cls, create(value))

    def __init__(self, value):
        # Call the parent class's __init__ method
        super(Url, self).__init__()

    def __add__(self, path: str):
        return self.append(path)

    def append(self, path: str) -> Url:
        return Url(append(self, path))


def create(url: str) -> str:
    """Create a Url.

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
        raise ValueError(
            f"URL must specify a scheme (e.g., http://example.com/__api__): {url}"
        )
    if not split.netloc:
        raise ValueError(
            f"URL must be absolute (e.g., http://example.com/__api__): {url}"
        )

    url = url.rstrip("/")
    if "/__api__" not in url:
        url = append(url, "__api__")

    return url


def append(url: str, path: str) -> str:
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
    >>> url = urls.create("http://example.com/__api__")
    >>> url + "path"
    http://example.com/__api__/path
    """
    path = str(path).strip("/")
    split = urlsplit(url, allow_fragments=False)
    new_path = posixpath.join(split.path, path)
    return urlunsplit(
        (split.scheme, split.netloc, new_path, split.query, None)
    )
