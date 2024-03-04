from requests import PreparedRequest
from requests.auth import AuthBase

from .config import Config


class Auth(AuthBase):
    def __init__(self, config: Config) -> None:
        self.config = config

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = f"Key {self.config.api_key}"
        return r
