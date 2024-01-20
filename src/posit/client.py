from requests import Session
from typing import Optional

from .auth import Auth
from .config import ConfigBuilder


class Client:
    def __init__(
        self, endpoint: Optional[str] = None, api_key: Optional[str] = None
    ) -> None:
        builder = ConfigBuilder()
        builder.set_api_key(api_key)
        builder.set_endpoint(endpoint)
        self._config = builder.build()
        self._session = Session()
        self._session.auth = Auth(self._config.api_key)

    def get(self, endpoint: str, *args, **kwargs):  # pragma: no cover
        return self._session.request(
            "GET", f"{self._config.endpoint}/{endpoint}", *args, **kwargs
        )
