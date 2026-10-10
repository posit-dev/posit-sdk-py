from __future__ import annotations

import posixpath
from urllib.parse import urljoin, urlsplit, urlunsplit


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
    joined = urlunsplit((split.scheme, split.netloc, new_path, split.query, None))
    # Defense-in-depth: ensure the resulting URL still points at the original
    # scheme+host+port. Guards against host-confusion if ``path`` is ever a
    # fully-qualified or protocol-relative URL (e.g. ``//evil`` or
    # ``https://evil``).
    _assert_same_origin(url, joined)
    return joined


def _assert_same_origin(base: str, resolved: str) -> None:
    """Raise ``ValueError`` if ``resolved`` is not same-origin with ``base``.

    Compares scheme, hostname, and port. Used to defend URL joining against
    user- or server-supplied fragments that would otherwise escape the
    configured Connect base URL.
    """
    base_split = urlsplit(base, allow_fragments=False)
    resolved_split = urlsplit(resolved, allow_fragments=False)
    if (
        base_split.scheme != resolved_split.scheme
        or base_split.hostname != resolved_split.hostname
        or base_split.port != resolved_split.port
    ):
        raise ValueError(
            f"Refusing to resolve URL to a different origin: base={base!r}, resolved={resolved!r}"
        )


def safe_urljoin(base: str, fragment: str) -> str:
    """Join ``fragment`` onto ``base`` without allowing host confusion.

    Unlike :func:`urllib.parse.urljoin`, a ``fragment`` beginning with ``/``,
    ``//host``, or ``https://host`` cannot change the scheme/host/port of the
    resolved URL. The fragment is first normalized to a relative path by
    stripping any leading ``/`` characters, then joined against ``base``. The
    result is asserted to be same-origin with ``base``.

    Parameters
    ----------
    base : str
        The trusted base URL (typically the configured Connect URL).
    fragment : str
        A path fragment, possibly user- or server-supplied.

    Returns
    -------
    str
        The joined URL, guaranteed to share scheme+host+port with ``base``.

    Raises
    ------
    ValueError
        If the joined URL would not be same-origin with ``base``.
    """
    normalized = str(fragment).lstrip("/")
    # Ensure base has a trailing slash so ``urljoin`` treats it as a directory
    # and appends rather than replacing the final path segment.
    base_with_slash = base if base.endswith("/") else base + "/"
    resolved = urljoin(base_with_slash, normalized)
    _assert_same_origin(base, resolved)
    return resolved
