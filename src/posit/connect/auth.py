from requests import PreparedRequest
from requests.auth import AuthBase

from .config import Config


class Auth(AuthBase):
    """_summary_

    Parameters
    ----------
    AuthBase : _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_  _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_ _type_
        _description_
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = f"Key {self._config.api_key}"
        return r
