"""Client connection for Posit Connect."""

from __future__ import annotations

from requests import Response, Session
from typing import Optional

from . import hooks, me, urls

from .auth import Auth
from .config import Config
from .oauth import OAuthIntegration
from .content import Content
from .metrics import Metrics
from .tasks import Tasks
from .users import User, Users
from .groups import Groups


class Client:
    """
    Client connection for Posit Connect.

    This class provides an interface to interact with the Posit Connect API,
    allowing for authentication, resource management, and data retrieval.

    Parameters
    ----------
    api_key : str, optional
        API key for authentication
    url : str, optional
        Sever API URL

    Attributes
    ----------
    content: Content
        Content resource.
    me: User
        Connect user resource.
    metrics: Metrics
        Metrics resource.
    tasks: Tasks
        Tasks resource.
    users: Users
        Users resource.
    version: str
        Server version.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        self.config = Config(api_key=api_key, url=url)
        session = Session()
        session.auth = Auth(config=self.config)
        session.hooks["response"].append(hooks.check_for_deprecation_header)
        session.hooks["response"].append(hooks.handle_errors)
        self.session = session

    @property
    def version(self) -> str:
        """
        The server version.

        Returns
        -------
        str
            The version of the Posit Connect server.
        """
        return self.get("server_settings").json()["version"]

    @property
    def me(self) -> User:
        """
        The connected user.

        Returns
        -------
        User
            The currently authenticated user.
        """
        return me.get(self.config, self.session)

    @property
    def oauth(self) -> OAuthIntegration:
        """
        An OAuthIntegration.

        Returns
        -------
        OAuthIntegration
            The OAuth integration instance.
        """
        return OAuthIntegration(config=self.config, session=self.session)

    @property
    def groups(self) -> Groups:
        """The groups resource interface.

        Returns
        -------
        Groups
            The groups resource interface.
        """
        return Groups(self.config, self.session)

    @property
    def tasks(self) -> Tasks:
        """
        The tasks resource interface.

        Returns
        -------
        tasks.Tasks
            The tasks resource instance.
        """
        return Tasks(self.config, self.session)

    @property
    def users(self) -> Users:
        """
        The users resource interface.

        Returns
        -------
        Users
            The users resource instance.
        """
        return Users(config=self.config, session=self.session)

    @property
    def content(self) -> Content:
        """
        The content resource interface.

        Returns
        -------
        Content
            The content resource instance.
        """
        return Content(config=self.config, session=self.session)

    @property
    def metrics(self) -> Metrics:
        """
        The Metrics API interface.

        The Metrics API is designed for capturing, retrieving, and managing
        quantitative measurements of Connect interactions. It is commonly used
        for monitoring and analyzing system performance, user behavior, and
        business processes. This API facilitates real-time data collection and
        accessibility, enabling organizations to make informed decisions based
        on key performance indicators (KPIs).

        Returns
        -------
        Metrics
            The metrics API instance.

        Examples
        --------
        >>> from posit import connect
        >>> client = connect.Client()
        >>> content_guid = "2243770d-ace0-4782-87f9-fe2aeca14fc8"
        >>> events = client.metrics.usage.find(content_guid=content_guid)
        >>> len(events)
        24
        """
        return Metrics(self.config, self.session)

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

        Parameters
        ----------
        exc_type : type
            The type of the exception raised (if any).
        exc_value : Exception
            The exception instance raised (if any).
        exc_tb : traceback
            The traceback for the exception raised (if any).
        """
        if hasattr(self, "session") and self.session is not None:
            self.session.close()

    def request(self, method: str, path: str, **kwargs) -> Response:
        """
        Send an HTTP request.

        A facade for [](`requests.request`) configured for the target server.

        Parameters
        ----------
        method : str
            The HTTP method to use for the request.
        path : str
            Appended to the url object attribute.
        **kwargs
            Additional keyword arguments passed to [](`requests.request`).

        Returns
        -------
        Response
            A [](`requests.Response`) object.
        """
        url = urls.append(self.config.url, path)
        return self.session.request(method, url, **kwargs)

    def get(self, path: str, **kwargs) -> Response:
        """
        Send a GET request.

        A facade for [](`requests.get`) configured for the target server.

        Parameters
        ----------
        path : str
            Appended to the configured base url.
        **kwargs
            Additional keyword arguments passed to [](`requests.get`).

        Returns
        -------
        Response
            A [](`requests.Response`) object.
        """
        url = urls.append(self.config.url, path)
        return self.session.get(url, **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        """
        Send a POST request.

        A facade for [](`requests.post`) configured for the target server.

        Parameters
        ----------
        path : str
            Appended to the configured base url.
        **kwargs
            Additional keyword arguments passed to [](`requests.post`).

        Returns
        -------
        Response
            A [](`requests.Response`) object.
        """
        url = urls.append(self.config.url, path)
        return self.session.post(url, **kwargs)

    def put(self, path: str, **kwargs) -> Response:
        """
        Send a PUT request.

        A facade for [](`requests.put`) configured for the target server.

        Parameters
        ----------
        path : str
            Appended to the configured base url.
        **kwargs
            Additional keyword arguments passed to [](`requests.put`).

        Returns
        -------
        Response
            A [](`requests.Response`) object.
        """
        url = urls.append(self.config.url, path)
        return self.session.put(url, **kwargs)

    def patch(self, path: str, **kwargs) -> Response:
        """
        Send a PATCH request.

        A facade for [](`requests.patch`) configured for the target server.

        Parameters
        ----------
        path : str
            Appended to the configured base url.
        **kwargs
            Additional keyword arguments passed to [](`requests.patch`).

        Returns
        -------
        Response
            A [](`requests.Response`) object.
        """
        url = urls.append(self.config.url, path)
        return self.session.patch(url, **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        """
        Send a DELETE request.

        A facade for [](`requests.delete`) configured for the target server.

        Parameters
        ----------
        path : str
            Appended to the configured base url.
        **kwargs
            Additional keyword arguments passed to [](`requests.delete`).

        Returns
        -------
        Response
            A [](`requests.Response`) object.
        """
        url = urls.append(self.config.url, path)
        return self.session.delete(url, **kwargs)
