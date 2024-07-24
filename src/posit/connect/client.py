"""Client connection for Posit Connect."""

from __future__ import annotations

from requests import Response, Session
from typing import Optional, overload

from . import hooks, me, urls

from .auth import Auth
from .config import Config
from .oauth import OAuthIntegration
from .content import Content
from .metrics import Metrics
from .tasks import Tasks
from .users import User, Users
from .groups import Groups
from .context import Context


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

    @overload
    def __init__(self) -> None:
        """Initialize a Client instance.

        Creates a client instance using credentials read from the environment.

        Environment Variables
        ---------------------
        CONNECT_SERVER - The Connect server URL.
        CONNECT_API_KEY - The API key credential for client authentication.

        Examples
        --------
        Client()
        """
        ...

    @overload
    def __init__(self, url: str) -> None:
        """Initialize a Client instance.

        Creates a client instance using a provided URL and API key credential read from the environment.

        Environment Variables
        ---------------------
        CONNECT_API_KEY - The API key credential for client authentication.

        Parameters
        ----------
        url : str
            The Connect server URL.

        Examples
        --------
        Client("https://connect.example.com)
        """
        ...

    @overload
    def __init__(self, url: str, api_key: str) -> None:
        """Initialize a Client instance.

        Parameters
        ----------
        url : str
            The Connect server URL.
        api_key : str
            The API key credential for client authentication.

        Examples
        --------
        >>> Client("https://connect.example.com", abcdefghijklmnopqrstuvwxyz012345")
        """
        ...

    @overload
    def __init__(self, *args, **kwargs) -> None:
        """Initialize a Client instance."""
        ...

    def __init__(self, *args, **kwargs) -> None:
        """Initialize a Client instance.

        Environment Variables
        ---------------------
        CONNECT_SERVER - The Connect server URL.
        CONNECT_API_KEY - The API key credential for client authentication.

        Parameters
        ----------
        *args
            Variable length argument list. Can accept:
            - (url: str)
                url: str
                    The Connect server URL.
            - (url: str, api_key: str)
                url: str
                    The Connect server URL.
                api_key: str
                    The API key credential for client authentication.

        **kwargs
            Keyword arguments. Can include 'url' and 'api_key'.

        Examples
        --------
        >>> Client()
        >>> Client("https://connect.example.com")
        >>> Client("https://connect.example.com", abcdefghijklmnopqrstuvwxyz012345")
        >>> Client(api_key=""abcdefghijklmnopqrstuvwxyz012345", url="https://connect.example.com")
        """
        api_key = None
        url = None
        if len(args) == 1 and isinstance(args[0], str):
            url = args[0]
        elif (
            len(args) == 2
            and isinstance(args[0], str)
            and isinstance(args[1], str)
        ):
            url = args[0]
            api_key = args[1]
        else:
            if "api_key" in kwargs and isinstance(kwargs["api_key"], str):
                api_key = kwargs["api_key"]
            if "url" in kwargs and isinstance(kwargs["url"], str):
                url = kwargs["url"]

        cfg = Config(api_key=api_key, url=url)
        session = Session()
        session.auth = Auth(config=cfg)
        session.hooks["response"].append(hooks.check_for_deprecation_header)
        session.hooks["response"].append(hooks.handle_errors)
        self.ctx = Context(api_key=cfg.api_key, session=session, url=cfg.url)

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
        return me.get(self.ctx)

    @property
    def oauth(self) -> OAuthIntegration:
        """
        An OAuthIntegration.

        Returns
        -------
        OAuthIntegration
            The OAuth integration instance.
        """
        return OAuthIntegration(self.ctx)

    @property
    def groups(self) -> Groups:
        """The groups resource interface.

        Returns
        -------
        Groups
            The groups resource interface.
        """
        return Groups(self.ctx)

    @property
    def tasks(self) -> Tasks:
        """
        The tasks resource interface.

        Returns
        -------
        tasks.Tasks
            The tasks resource instance.
        """
        return Tasks(self.ctx)

    @property
    def users(self) -> Users:
        """
        The users resource interface.

        Returns
        -------
        Users
            The users resource instance.
        """
        return Users(self.ctx)

    @property
    def content(self) -> Content:
        """
        The content resource interface.

        Returns
        -------
        Content
            The content resource instance.
        """
        return Content(self.ctx)

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
        return Metrics(self.ctx)

    def __del__(self):
        """Close the session when the Client instance is deleted."""
        if hasattr(self, "ctx") and self.ctx is not None:
            self.ctx.session.close()

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
        if hasattr(self, "ctx") and self.ctx is not None:
            self.ctx.session.close()

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
        url = urls.append(self.ctx.url, path)
        return self.ctx.session.request(method, url, **kwargs)

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
        url = urls.append(self.ctx.url, path)
        return self.ctx.session.get(url, **kwargs)

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
        url = urls.append(self.ctx.url, path)
        return self.ctx.session.post(url, **kwargs)

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
        url = urls.append(self.ctx.url, path)
        return self.ctx.session.put(url, **kwargs)

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
        url = urls.append(self.ctx.url, path)
        return self.ctx.session.patch(url, **kwargs)

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
        url = urls.append(self.ctx.url, path)
        return self.ctx.session.delete(url, **kwargs)
