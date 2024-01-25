from requests import PreparedRequest
from requests.auth import AuthBase


class Auth(AuthBase):
    def __init__(self, key: str) -> None:
        self.key = key

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = f"Key {self.key}"
        return r
