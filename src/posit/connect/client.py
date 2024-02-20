from __future__ import annotations

import os
from requests import Session
from typing import Optional

from . import hooks

from .auth import Auth
from .config import Config
from .oauth import OAuthIntegration
from .users import User, Users, CachedUsers


class Client:
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        """
        Initialize the Client instance.

        Args:
            api_key (str, optional): API key for authentication. Defaults to None.
            endpoint (str, optional): API endpoint URL. Defaults to None.
        """
        # Create a Config object.
        config = Config(api_key=api_key, endpoint=endpoint)
        # Create a Session object for making HTTP requests.
        session = Session()
        # Authenticate the session using the provided Config.
        session.auth = Auth(config=config)
        # Add error handling hooks to the session.
        session.hooks["response"].append(hooks.handle_errors)

        # Store the Config and Session objects.
        self._config = config
        self._session = session

        # Internal properties for storing public resources
        self._current_user: Optional[User] = None
        self._oauth: Optional[OAuthIntegration] = None


    # Connect sets the value of the environment variable RSTUDIO_PRODUCT = CONNECT
    # when content is running on a Connect server. Use this var to determine if the
    # client SDK was initialized from a piece of content running on a Connect server.
    def is_local(self) -> bool:
        return not os.getenv("RSTUDIO_PRODUCT") == "CONNECT"


    @property
    def me(self) -> User:
        if self._current_user is None:
            endpoint = os.path.join(self._config.endpoint, "v1/user")
            response = self._session.get(endpoint)
            self._current_user = User(**response.json())
        return self._current_user


    @property
    def oauth(self) -> OAuthIntegration:
        if self._oauth is None:
            self._oauth = OAuthIntegration(client=self)
        return self._oauth


    @property
    def users(self) -> CachedUsers:
        return Users(client=self)


    def __del__(self):
        """
        Close the session when the Client instance is deleted.
        """
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._session.close()
