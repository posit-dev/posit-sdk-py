import posixpath

from urllib.parse import urljoin, urlparse


class Url:
    def __init__(self, url: str) -> None:
        """
        Initializes a Url object.

        Args:
            url (str): The URL to be used.

        Returns:
            None
        """
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("url must be an absolute URL: {url}")

        if parsed.path != "/__api__":
            self.url = urljoin(url, "/__api__")
        else:
            self.url = url

    def append(self, path: str = "") -> str:
        """
        Appends a path to the URL.

        Args:
            path (str): The path to be appended to the URL. Defaults to an empty string.

        Returns:
            str: The updated URL with the appended path.
        """
        if path:
            parsed = urlparse(path)
            if parsed.scheme or parsed.netloc:
                raise ValueError(
                    f"path must be a relative URL, not an absolute URL: {path}"
                )
            return urljoin(self.url, posixpath.join(urlparse(self.url).path, path))
        return self.url
