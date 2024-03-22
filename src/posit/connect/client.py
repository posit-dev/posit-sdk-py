from __future__ import annotations

from requests import Response, Session
from typing import Optional

from . import hooks, me, urls

from .auth import Auth
from .config import Config
from .oauth import OAuthIntegration
from .content import Content
from .users import User, Users


class Client:
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
        if self._server_settings is None:
            self._server_settings = self.get("server_settings").json()
        return self._server_settings["version"]

    @property
    def me(self) -> User:
        return me.get(self.config, self.session)

    @property
    def oauth(self) -> OAuthIntegration:
        return OAuthIntegration(config=self.config, session=self.session)

    @property
    def users(self) -> Users:
        return Users(config=self.config, session=self.session)

    @property
    def content(self) -> Content:
        return Content(config=self.config, session=self.session)

    def __del__(self):
        """
        Close the session when the Client instance is deleted.
        """
        if hasattr(self, "session") and self.session is not None:
            self.session.close()

    def __enter__(self):
        """
        Enter method for using the client as a context manager.
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """
        Closes the session if it exists.

        Args:
            exc_type: The type of the exception raised (if any).
            exc_value: The exception instance raised (if any).
            exc_tb: The traceback for the exception raised (if any).
        """
        if hasattr(self, "session") and self.session is not None:
            self.session.close()

    def request(self, method: str, path: str, **kwargs) -> Response:
        """
        Sends an HTTP request to the specified path using the given method.

        Args:
            method (str): The HTTP method to use for the request.
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to pass to the underlying session's request method.

        Returns:
            Response: The response object containing the server's response to the request.
        """
        url = urls.append_path(self.config.url, path)
        return self.session.request(method, url, **kwargs)

    def get(self, path: str, **kwargs) -> Response:
        """
        Send a GET request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `get` method.

        Returns:
            Response: The response object.

        """
        url = urls.append_path(self.config.url, path)
        return self.session.get(url, **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        """
        Send a POST request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `post` method.

        Returns:
            Response: The response object.

        """
        url = urls.append_path(self.config.url, path)
        return self.session.post(url, **kwargs)

    def put(self, path: str, **kwargs) -> Response:
        """
        Send a PUT request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `put` method.

        Returns:
            Response: The response object.

        """
        url = urls.append_path(self.config.url, path)
        return self.session.put(url, **kwargs)

    def patch(self, path: str, **kwargs) -> Response:
        """
        Send a PATCH request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `patch` method.

        Returns:
            Response: The response object.

        """
        url = urls.append_path(self.config.url, path)
        return self.session.patch(url, **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        """
        Send a DELETE request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `delete` method.

        Returns:
            Response: The response object.

        """
        url = urls.append_path(self.config.url, path)
        return self.session.delete(url, **kwargs)
