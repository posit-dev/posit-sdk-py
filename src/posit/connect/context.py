from typing import Final

import requests


class Context:
    def __init__(
        self, *, api_key: str, session: requests.Session, url: str
    ) -> None:
        self.api_key: Final[str] = api_key
        self.session: Final[requests.Session] = session
        self.url: Final[str] = url
