from requests import Session
from typing import Optional

from . import hooks

from .auth import Auth
from .config import ConfigBuilder
from .users import Users


class Client:
    users: Users

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        builder = ConfigBuilder()
        if api_key:
            builder.set_api_key(api_key)
        if endpoint:
            builder.set_endpoint(endpoint)
        self._config = builder.build()

        if self._config.api_key is None:
            raise ValueError("Invalid value for 'api_key': Must be a non-empty string.")
        if self._config.endpoint is None:
            raise ValueError(
                "Invalid value for 'endpoint': Must be a non-empty string."
            )

        self._session = Session()
        self._session.hooks["response"].append(hooks.handle_errors)
        self._session.auth = Auth(self._config.api_key)
        self.users = Users(self._config.endpoint, self._session)
