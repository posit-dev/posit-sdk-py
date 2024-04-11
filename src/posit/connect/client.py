"""Contains the Client class."""

from __future__ import annotations

from requests import Response, Session
from typing import Optional

from . import hooks, me, urls

from .auth import Auth
from .config import Config
from .oauth import OAuthIntegration
from .content import Content
from .usage import Usage
from .users import User, Users
from .visits import Visits


class Client:
    """Main interface for Posit Connect."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Initialize the Client instance.

        Args:
            api_key (str, optional): API key for authentication. Defaults to None.
            url (str, optional): API url URL. Defaults to None.
        """
        # Create a Config object.
        self.config = Config(api_key=api_key, url=url)
        # Create a Session object for making HTTP requests.
        session = Session()
        # Authenticate the session using the provided Config.
        session.auth = Auth(config=self.config)
        # Add error handling hooks to the session.
        session.hooks["response"].append(hooks.handle_errors)

        # Store the Session object.
        self.session = session

        # Internal attributes to hold settings we fetch lazily
        self._server_settings = None

    @property
    def connect_version(self):
        """The server version.

        Return:
            str
        """
        if self._server_settings is None:
            self._server_settings = self.get("server_settings").json()
        return self._server_settings["version"]

    @property
    def me(self) -> User:
        """The connected user.

        Returns
        -------
        User
        """
        return me.get(self.config, self.session)

    @property
    def oauth(self) -> OAuthIntegration:
        """An OAuthIntegration.

        Returns
        -------
        OAuthIntegration
        """
        return OAuthIntegration(config=self.config, session=self.session)

    @property
    def users(self) -> Users:
        """The users resource interface.

        Returns
        -------
        Users
        """
        return Users(config=self.config, session=self.session)

    @property
    def content(self) -> Content:
        """The content resource interface.

        Returns
        -------
        Content
        """
        return Content(config=self.config, session=self.session)

    @property
    def usage(self) -> Usage:
        return Usage(self.config, self.session)

    @property
    def visits(self) -> Visits:
        return Visits(self.config, self.session)

    def __del__(self):
        """Close the session when the Client instance is deleted."""
        if hasattr(self, "session") and self.session is not None:
            self.session.close()

    def __enter__(self):
        """Enter method for using the client as a context manager."""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """
        Close the session if it exists.

        Args:
            exc_type: The type of the exception raised (if any).
            exc_value: The exception instance raised (if any).
            exc_tb: The traceback for the exception raised (if any).
        """
        if hasattr(self, "session") and self.session is not None:
            self.session.close()

    def request(self, method: str, path: str, **kwargs) -> Response:
        """
        Send an HTTP request.

        A facade for requests.Session.request.

        Args:
            method (str): The HTTP method to use for the request.
            path (str): Appended to the url object attribute.
            **kwargs: Additional keyword arguments passed to requests.Session.post.

        Returns
        -------
            Response: A requests.Response object.
        """
        url = urls.append(self.config.url, path)
        return self.session.request(method, url, **kwargs)

    def get(self, path: str, **kwargs) -> Response:
        """
        Send a GET request.

        Args:
            path (str): Appended to the configured base url.
            **kwargs: Additional keyword arguments passed to requests.Session.get.

        Returns
        -------
            Response: A requests.Response object.

        """
        url = urls.append(self.config.url, path)
        return self.session.get(url, **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        """
        Send a POST request.

        Args:
            path (str): Appended to the configured base url.
            **kwargs: Additional keyword arguments passed to requests.Session.post.

        Returns
        -------
            Response: A requests.Response object.

        """
        url = urls.append(self.config.url, path)
        return self.session.post(url, **kwargs)

    def put(self, path: str, **kwargs) -> Response:
        """
        Send a PUT request.

        Args:
            path (str): Appended to the configured base url.
            **kwargs: Additional keyword arguments passed to requests.Session.put.

        Returns
        -------
            Response: A requests.Response object.

        """
        url = urls.append(self.config.url, path)
        return self.session.put(url, **kwargs)

    def patch(self, path: str, **kwargs) -> Response:
        """
        Send a PATCH request.

        Args:
            path (str): Appended to the configured base url.
            **kwargs: Additional keyword arguments passed to requests.Session.patch.

        Returns
        -------
            Response: A requests.Response object.

        """
        url = urls.append(self.config.url, path)
        return self.session.patch(url, **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        """
        Send a DELETE request.

        Args:
            path (str): Appended to the configured base url.
            **kwargs: Additional keyword arguments passed to requests.Session.delete.

        Returns
        -------
            Response: A requests.Response object.

        """
        url = urls.append(self.config.url, path)
        return self.session.delete(url, **kwargs)
