"""URL handling for Workbench."""

from __future__ import annotations

import posixpath
from urllib.parse import urlsplit, urlunsplit


class Url(str):
    """URL string subclass with proper path joining."""

    def __new__(cls, value: str):
        url = _create(value)
        return super(Url, cls).__new__(cls, url)

    def __add__(self, path: str):
        return self.append(path)

    def append(self, path: str) -> Url:
        """Append a path to the URL."""
        return Url(_append(self, path))


def _create(url: str) -> str:
    """Validate and normalize a URL."""
    split = urlsplit(url, allow_fragments=False)
    if not split.scheme:
        raise ValueError(f"URL must specify a scheme (e.g., https://example.com): {url}")
    if not split.netloc:
        raise ValueError(f"URL must be absolute (e.g., https://example.com): {url}")
    return url.rstrip("/")


def _append(url: str, path: str) -> str:
    """Append a path to a URL using posixpath.join to preserve base paths."""
    path = str(path).strip("/")
    split = urlsplit(url, allow_fragments=False)
    new_path = posixpath.join(split.path, path)
    return urlunsplit((split.scheme, split.netloc, new_path, split.query, None))
