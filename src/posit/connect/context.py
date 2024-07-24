import requests


class Context:
    def __init__(
        self, *, api_key: str, session: requests.Session, url: str
    ) -> None:
        self.api_key = api_key
        self.session = session
        self.url = url
