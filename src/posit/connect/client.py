from __future__ import annotations

from requests import Response, Session
from typing import Optional

from . import hooks

from .auth import Auth
from .config import Config
from .users import Users, CachedUsers


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

        # Initialize the Users instance.
        self.users: CachedUsers = Users(config=self.config, session=session)
        # Store the Session object.
        self.session = session

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

    def get(self, path: str, **kwargs) -> Response:
        """
        Send a GET request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `get` method.

        Returns:
            Response: The response object.

        """
        return self.session.get(self.config.url.append(path), **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        """
        Send a POST request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `post` method.

        Returns:
            Response: The response object.

        """
        return self.session.post(self.config.url.append(path), **kwargs)

    def put(self, path: str, **kwargs) -> Response:
        """
        Send a PUT request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `put` method.

        Returns:
            Response: The response object.

        """
        return self.session.put(self.config.url.append(path), **kwargs)

    def patch(self, path: str, **kwargs) -> Response:
        """
        Send a PATCH request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `patch` method.

        Returns:
            Response: The response object.

        """
        return self.session.patch(self.config.url.append(path), **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        """
        Send a DELETE request to the specified path.

        Args:
            path (str): The path to send the request to.
            **kwargs: Additional keyword arguments to be passed to the underlying session's `delete` method.

        Returns:
            Response: The response object.

        """
        return self.session.delete(self.config.url.append(path), **kwargs)
